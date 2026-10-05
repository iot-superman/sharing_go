import json, secrets
import urllib.parse
import urllib.request
from functools import lru_cache
from datetime import date, time, datetime
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from .models import Profile,Ride,RideMember,Message,Location

def home(request): return render(request,'index.html')
def health(request): return JsonResponse({'ok':True})

@lru_cache(maxsize=512)
def _reverse_geocode_cached(lat6, lng6):
    """
    2026-10-05 新增：使用 OSM Nominatim 做「經緯度 -> 地址」反向地理編碼。
    - 只在使用者明確點選位置時呼叫，不在拖曳地圖時連續查詢。
    - 用 6 位小數座標做快取，避免重複查詢同一點。
    - 回傳 display_name 與拆解後 address，前端用 display_name 回填輸入框。
    """
    params = urllib.parse.urlencode({
        'format': 'jsonv2',
        'lat': lat6,
        'lon': lng6,
        'zoom': 18,
        'addressdetails': 1,
        'accept-language': 'zh-TW,zh;q=0.9,en;q=0.7',
    })
    url = f'https://nominatim.openstreetmap.org/reverse?{params}'
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'CarpoolGoDjango/1.0 (educational project)',
            'Accept': 'application/json',
        },
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        return json.loads(resp.read().decode('utf-8'))


def reverse_geocode(request):
    """前端精確選點後取得人類可讀地址。"""
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    try:
        lat = float(request.GET.get('lat', ''))
        lng = float(request.GET.get('lng', ''))
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError('out of range')
        # 六位小數約可到 0.1 公尺等級，已遠高於一般 GPS 精度。
        lat6 = f'{lat:.6f}'
        lng6 = f'{lng:.6f}'
        data = _reverse_geocode_cached(lat6, lng6)
        display = str(data.get('display_name') or '').strip()
        return JsonResponse({
            'ok': bool(display),
            'displayName': display,
            'lat': float(data.get('lat', lat)),
            'lng': float(data.get('lon', lng)),
            'address': data.get('address') or {},
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': f'地址解析失敗：{e}'}, status=502)

@lru_cache(maxsize=256)
def _osrm_route_cached(start_lat6, start_lng6, end_lat6, end_lng6):
    """
    2026-10-05 新增：取得開車路線幾何，供前端 Leaflet 畫出實際道路路徑。
    使用 OSRM 公開示範服務；只在建立/顯示共乘路線時查詢，並以座標快取避免重複請求。
    """
    coords = f'{start_lng6},{start_lat6};{end_lng6},{end_lat6}'
    params = urllib.parse.urlencode({
        'overview': 'full',
        'geometries': 'geojson',
        'steps': 'false',
    })
    url = f'https://router.project-osrm.org/route/v1/driving/{coords}?{params}'
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'CarpoolGoDjango/1.0 (educational project)',
            'Accept': 'application/json',
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))


@lru_cache(maxsize=512)
def _forward_geocode_cached(query):
    """
    地址/地名 -> 經緯度。
    2026-10-05：回傳最多 5 筆候選，供使用者「輸入文字 -> 按搜尋 -> 點選地址」。
    注意：OSMF 公開 Nominatim 禁止 client-side autocomplete，
    因此本專案不會在每次 keyup 自動查詢，只在使用者按搜尋/Enter 時查一次。
    """
    params = urllib.parse.urlencode({
        'format': 'jsonv2',
        'q': query,
        'limit': 5,
        'addressdetails': 1,
        'dedupe': 1,
        'countrycodes': 'tw',
        'accept-language': 'zh-TW,zh;q=0.9,en;q=0.7',
    })
    url = f'https://nominatim.openstreetmap.org/search?{params}'
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'CarpoolGoDjango/1.2 (educational project)',
            'Accept': 'application/json',
        },
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        return json.loads(resp.read().decode('utf-8'))


def forward_geocode(request):
    """使用者主動輸入地址/地名後搜尋座標；回傳多筆候選並保留舊版第一筆欄位相容性。"""
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    query = str(request.GET.get('q') or '').strip()
    if not query:
        return JsonResponse({'ok': False, 'error': '缺少 q'}, status=400)
    try:
        rows = _forward_geocode_cached(query[:200])
        if not rows:
            return JsonResponse({'ok': False, 'error': '找不到位置', 'results': []}, status=404)

        results = []
        for row in rows[:5]:
            try:
                results.append({
                    'lat': float(row['lat']),
                    'lng': float(row['lon']),
                    'displayName': row.get('display_name') or query,
                    'type': row.get('type') or '',
                    'category': row.get('category') or '',
                })
            except (KeyError, TypeError, ValueError):
                continue

        if not results:
            return JsonResponse({'ok': False, 'error': '找不到有效位置', 'results': []}, status=404)

        first = results[0]
        return JsonResponse({
            'ok': True,
            'lat': first['lat'],
            'lng': first['lng'],
            'displayName': first['displayName'],
            'results': results,
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': f'地址搜尋失敗：{e}'}, status=502)


def route_preview(request):
    """回傳集合點到目的地的道路路線 GeoJSON、距離與預估時間。"""
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    try:
        start_lat = float(request.GET.get('start_lat', ''))
        start_lng = float(request.GET.get('start_lng', ''))
        end_lat = float(request.GET.get('end_lat', ''))
        end_lng = float(request.GET.get('end_lng', ''))
        for lat in (start_lat, end_lat):
            if not -90 <= lat <= 90:
                raise ValueError('latitude out of range')
        for lng in (start_lng, end_lng):
            if not -180 <= lng <= 180:
                raise ValueError('longitude out of range')

        data = _osrm_route_cached(
            f'{start_lat:.6f}', f'{start_lng:.6f}',
            f'{end_lat:.6f}', f'{end_lng:.6f}',
        )
        routes = data.get('routes') or []
        if data.get('code') != 'Ok' or not routes:
            return JsonResponse({'ok': False, 'error': '找不到可行駛路線'}, status=404)
        route = routes[0]
        geometry = route.get('geometry') or {}
        if geometry.get('type') != 'LineString' or not geometry.get('coordinates'):
            return JsonResponse({'ok': False, 'error': '路線幾何資料不完整'}, status=502)
        return JsonResponse({
            'ok': True,
            'geometry': geometry,
            'distanceMeters': round(float(route.get('distance') or 0), 1),
            'durationSeconds': round(float(route.get('duration') or 0), 1),
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': f'路線規劃失敗：{e}'}, status=502)

def body(request):
    try:return json.loads(request.body or b'{}')
    except:return {}
def profile(request, create=True):
    cid=request.headers.get('X-Client-ID') or request.GET.get('client_id')
    if not cid: return None
    p=Profile.objects.filter(client_id=cid).first()
    if not p and create:
        p=Profile.objects.create(client_id=cid,nickname='使用者-'+cid[-4:].upper())
    return p
def ride_json(r,p=None):
    # 2026-10-05 修正：Ride 剛建立時 DateField / TimeField 可能仍保留前端傳入的字串，
    # 不可直接假設 ride_time 一定有 strftime()。這裡同時相容字串與 datetime.time。
    ms=list(RideMember.objects.filter(ride=r).select_related('profile'))
    current=len(ms); remaining=max(0,r.max_people-current)
    ride_date_text = r.ride_date.isoformat() if hasattr(r.ride_date, 'isoformat') else str(r.ride_date)
    ride_time_text = r.ride_time.strftime('%H:%M') if hasattr(r.ride_time, 'strftime') else str(r.ride_time)[:5]
    return {'id':r.id,'ownerId':r.owner.client_id,'ownerName':r.owner.nickname,'isMine':bool(p and r.owner_id==p.id),'mode':r.mode,'status':r.status,'date':ride_date_text,'time':ride_time_text,'maxPeople':r.max_people,'currentPeople':current,'remaining':remaining,'meeting':{'name':r.meeting_name,'lat':r.meeting_lat,'lng':r.meeting_lng},'destination':{'name':r.destination_name,'lat':r.destination_lat,'lng':r.destination_lng},'estimatedTotal':r.estimated_total,'pricePerPerson':r.price_per_person,'plate':r.plate,'vehicle':r.vehicle,'note':r.note,'locked':r.locked,'members':[{'clientId':m.profile.client_id,'nickname':m.profile.nickname,'role':m.role} for m in ms]}
@csrf_exempt
def me(request):
    p=profile(request)
    if not p:return HttpResponseBadRequest('X-Client-ID required')
    if request.method=='PATCH':
        d=body(request); n=str(d.get('nickname','')).strip()
        if n:p.nickname=n[:80];p.save(update_fields=['nickname','updated_at'])
    return JsonResponse({'clientId':p.client_id,'nickname':p.nickname})
@csrf_exempt
def rides(request):
    p=profile(request)
    if not p:return HttpResponseBadRequest('X-Client-ID required')
    if request.method=='GET':
        qs=Ride.objects.exclude(status='cancelled').select_related('owner').prefetch_related('ridemember_set__profile')[:100]
        return JsonResponse({'rides':[ride_json(r,p) for r in qs]})
    if request.method=='POST':
        d=body(request)
        try:
            # 2026-10-05 修正：HTML date/time 輸入值是字串。
            # 先轉成真正的 Python date / time，避免 Ride.objects.create() 後，
            # 記憶體中的 r.ride_time 還是 str，ride_json() 呼叫 strftime 時出錯。
            date_text = str(d.get('date') or '').strip()
            time_text = str(d.get('time') or '').strip()
            ride_date_value = datetime.strptime(date_text, '%Y-%m-%d').date() if date_text else date.today()
            ride_time_value = datetime.strptime(time_text, '%H:%M').time() if time_text else time(16,50)

            with transaction.atomic():
                r=Ride.objects.create(owner=p,mode=d.get('mode','taxi'),ride_date=ride_date_value,ride_time=ride_time_value,max_people=max(2,min(8,int(d.get('maxPeople',3)))),meeting_name=d.get('meetingName') or '目前位置附近集合點',meeting_lat=d.get('meetingLat'),meeting_lng=d.get('meetingLng'),destination_name=d.get('destinationName') or '埔心火車站後站',destination_lat=d.get('destinationLat'),destination_lng=d.get('destinationLng'),estimated_total=max(0,int(d.get('estimatedTotal',120))),price_per_person=max(0,int(d.get('pricePerPerson',0))),plate=d.get('plate',''),vehicle=d.get('vehicle',''),note=d.get('note',''),locked=bool(d.get('locked',True)))
                RideMember.objects.create(ride=r,profile=p,role='owner')
            return JsonResponse({'ride':ride_json(r,p)},status=201)
        except ValueError:
            return JsonResponse({'error':'日期或時間格式錯誤，日期請使用 YYYY-MM-DD，時間請使用 HH:MM。'},status=400)
        except Exception as e:
            return JsonResponse({'error':str(e)},status=400)
    return HttpResponseNotAllowed(['GET','POST'])
@csrf_exempt
def ride_detail(request,ride_id):
    p=profile(request); r=get_object_or_404(Ride,id=ride_id)
    return JsonResponse({'ride':ride_json(r,p)})
@csrf_exempt
def join_ride(request,ride_id):
    if request.method!='POST':return HttpResponseNotAllowed(['POST'])
    p=profile(request); 
    with transaction.atomic():
        r=Ride.objects.select_for_update().get(id=ride_id)
        if r.status!='open':return JsonResponse({'error':'此共乘目前不可加入'},status=409)
        if r.owner_id==p.id:return JsonResponse({'error':'不能加入自己建立的共乘'},status=409)
        if RideMember.objects.filter(ride=r,profile=p).exists():return JsonResponse({'ride':ride_json(r,p)})
        if RideMember.objects.filter(ride=r).count()>=r.max_people:
            r.status='full';r.save(update_fields=['status','updated_at']);return JsonResponse({'error':'已額滿'},status=409)
        RideMember.objects.create(ride=r,profile=p)
        if RideMember.objects.filter(ride=r).count()>=r.max_people:r.status='full';r.save(update_fields=['status','updated_at'])
    return JsonResponse({'ride':ride_json(r,p)})
@csrf_exempt
def cancel_ride(request,ride_id):
    if request.method!='POST':return HttpResponseNotAllowed(['POST'])
    p=profile(request);r=get_object_or_404(Ride,id=ride_id)
    if r.owner_id!=p.id:return HttpResponseForbidden('only owner')
    r.status='cancelled';r.save(update_fields=['status','updated_at']);return JsonResponse({'ok':True})
@csrf_exempt
def my_trip(request):
    p=profile(request)
    # 2026-10-05 修正：目前行程以「使用者最近加入的那一筆共乘」為準，
    # 不再用共乘建立時間排序。這樣即使加入較早建立的募集，也會立刻切到剛加入的行程地圖。
    m=RideMember.objects.filter(
        profile=p,
        ride__status__in=['open','full']
    ).select_related('ride__owner').order_by('-joined_at','-id').first()
    return JsonResponse({'ride':ride_json(m.ride,p) if m else None})
def message_json(m):
    return {
        'id': m.id,
        'senderId': m.sender.client_id,
        'senderName': m.sender.nickname,
        'text': m.text,
        'createdAt': m.created_at.isoformat(),
    }

@csrf_exempt
def messages(request,ride_id):
    p=profile(request);r=get_object_or_404(Ride,id=ride_id)
    if not RideMember.objects.filter(ride=r,profile=p).exists():return HttpResponseForbidden('not member')
    created = None
    if request.method=='POST':
        txt=str(body(request).get('text','')).strip()
        if not txt:return JsonResponse({'error':'empty'},status=400)
        created=Message.objects.create(ride=r,sender=p,text=txt[:1000])
        # 重新帶 sender，讓回傳格式和 GET 完全一致。
        created.sender=p
    qs=Message.objects.filter(ride=r).select_related('sender').order_by('-id')[:100]
    arr=[message_json(m) for m in reversed(qs)]
    payload={'messages':arr}
    if created is not None:
        payload['message']=message_json(created)
    return JsonResponse(payload)
@csrf_exempt
def locations(request,ride_id):
    p=profile(request);r=get_object_or_404(Ride,id=ride_id)
    if not RideMember.objects.filter(ride=r,profile=p).exists():return HttpResponseForbidden('not member')
    if request.method=='POST':
        d=body(request)
        try: Location.objects.update_or_create(ride=r,profile=p,defaults={'lat':float(d['lat']),'lng':float(d['lng']),'accuracy':d.get('accuracy')})
        except:return JsonResponse({'error':'invalid location'},status=400)
    qs=Location.objects.filter(ride=r).select_related('profile')
    return JsonResponse({'locations':[{'clientId':x.profile.client_id,'nickname':x.profile.nickname,'lat':x.lat,'lng':x.lng,'accuracy':x.accuracy,'updatedAt':x.updated_at.isoformat()} for x in qs]})
