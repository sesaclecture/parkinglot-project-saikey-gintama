from datetime import datetime



parking_cell = {} 
for floor in range(ord('A'), ord('J') + 1):  # A~J 층
    for num in range(1, 11):                 # 1~10번 자리
        loca = f"{chr(floor)}{num}"
        parking_cell[loca] = 0  # 0: 비어있음, 1: 사용 중

season_pass_list = ['12가3456', 
                    '34나5678', 
                    ]   # 정기권 차량 목록
parking = {'12가3456':{'in_time':datetime(2025, 8, 31, 12, 0, 0), 'ss_pass':True, 'loca':'D10'},
           '56다7891':{'in_time':datetime(2025, 8, 31, 7, 7, 7), 'ss_pass':False, 'loca':'A3'}, 
           }   # 실시간 주차 목록
log = [ {'plate':'12가3456', 'in_time':datetime(2025, 8, 29, 8, 8, 8), 'out_time':datetime(2025, 8, 29, 17, 17, 17), 'ss_pass':True, 'loca':'D10'},
        {'plate':'78라9101', 'in_time':datetime(2025, 8, 27, 7, 7, 7), 'out_time':datetime(2025, 8, 27, 12, 0, 0), 'ss_pass':False, 'loca':'A8'},
        {'plate':'34나5678', 'in_time':datetime(2025, 8, 24, 7, 0, 0), 'out_time':datetime(2025, 8, 24, 20, 20, 20), 'ss_pass':True, 'loca':'F1'},
        ]   # 역대 주차 기록 



def update_park():
    """실시간 주차 목록 반영"""
    for fkey, fvalue in parking.items():
        full = fvalue['loca'] 
        if full in parking_cell:
            parking_cell[full] = 1



def in_sspark(plate, now, loca=None):
    """정기권 입차 시스템: 원하는 자리 입력 받기"""
    WEB_mode = (loca is not None)

    while True: 
        loca = input("location (A1~J10): ") if loca is None else loca
        if loca not in parking_cell: # 없는 자리면 
            print("❌ Sorry, That spot doesn't exist")
            if WEB_mode: return
            loca = None
            continue 
        elif parking_cell[loca] == 1: # 이미 주차된 자리면 
            print("☠️ Sorry. That spot is already full ☠️")
            if WEB_mode: return
            loca = None
            continue

        print(f"😎 You are parking! Have a good day 😎")
        parking[plate] = {'in_time':now, # 실시간 주차 목록에 추가 
                        'ss_pass':True, 
                        'loca':loca}
        parking_cell[loca] = 1  # 주차된 자리 표시
        #print(parking_cell)
        print(f"🚗 {plate} is entering to {loca} 🚗")
        break



def in_park(plate, now):
    """일반 입차 시스템: 빈자리 강제 추천"""
    update_park()
    loca = None
    for ekey, evalue in parking_cell.items():
        if evalue == 0: # 가장 빠른 빈자리 
            loca = ekey
            break

    print(f"😎 You are parking! Have a good day 😎")
    parking[plate] = {'in_time':now, # 실시간 주차 목록에 추가 
                    'ss_pass':False, 
                    'loca':loca}
    parking_cell[loca] = 1  # 주차된 자리 표시
    #print(parking_cell)
    print(f"🚗 {plate} is entering to {loca} 🚗")



def out_park(plate, now):
    """출차 시스템"""
    in_time = parking[plate]['in_time']
    ss_pass = parking[plate]['ss_pass']
    hour = (now - in_time).total_seconds() / 3600
    fee = int(hour * (1500 if ss_pass else 3000)) # 요금 계산 
    print(f"💲 You were parked for {hour:.2f} hour. Please fee {fee} won 💲")

    loca = parking[plate]['loca']
    parking_cell[loca] = 0        # 주차 표시 제거 
    log.append( {'plate':plate,   # 역대 주차 기록에 추가 
                'in_time':in_time, 
                'out_time':now, 
                'ss_pass':ss_pass, 
                'loca':loca} )
    del parking[plate]            # 실시간 주차 목록에서 삭제 
    #print(parking_cell)
    print("😁 Thank you for using our parking lot. See you! 😁")



def parking_system(plate=None, in_confirm=None, out_confirm=None, pass_confirm=None, loca=None, now=None): 
    """전체 process"""
    update_park()
    plate = input("What's your plate number? : ") if plate is None else plate
    now = now or datetime.now()
    
    if plate in parking: # 주차 중이면
        out_confirm = input("출차하실? (y/n)") if out_confirm is None else out_confirm
        if out_confirm == 'y': # ----- 출차 시스템 -----
            out_park(plate, now)

    else: # 새로 들어온거면 
        in_confirm = input("입차하실? (y/n)") if in_confirm is None else in_confirm
        if in_confirm == 'y': # ----- 입차 시스템 -----
            ss_pass = plate in season_pass_list
            if ss_pass : # 정기권이면 
                in_sspark(plate, now, loca=loca)    
            else: # 일반이면
                pass_confirm = input("Do you want to join us? We can give you 50% discount! (y/n)") if pass_confirm is None else pass_confirm
                if pass_confirm == 'y': # ----- 정기권 시스템 -----
                    season_pass_list.append(plate) # 정기권 차량 목록에 추가 
                    print("🎉 Welcome to our porking lot!!! 🎉")
                    in_sspark(plate, now, loca=loca)
                else: # 가입 안하면 
                    in_park(plate, now)



# ============ 웹 레이어 ============
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.after_request
def _cors(resp):
    """외부(origin)에서 오는 요청 허용"""
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp


@app.get("/state")
def http_state():
    """프런트가 2초마다 보는 상태"""
    update_park()

    parking_json = {}
    for key, value in parking.items():
        parking_json[key] = { # datetime을 문자열로 변환 
            "in_time": value["in_time"].isoformat() if isinstance(value["in_time"], datetime) else value["in_time"],
            "ss_pass": value["ss_pass"],
            "loca": value["loca"]}

    return jsonify({"grid": dict(parking_cell),  # 현재 전역 grid 그대로 노출
                    "parking": parking_json,
                    "season_pass_list": list(season_pass_list)})



@app.post("/check")
def http_check():
    """정기권 여부 체크"""
    data = request.get_json(silent=True) or {}
    plate = (data.get("plate") or "").strip()
    if not plate:
        return jsonify(detail="plate is empty"), 400
    if plate in parking:
        rec = parking[plate]
        return jsonify(status="in",
                       loca=rec["loca"],
                       ss_pass=rec["ss_pass"],
                       in_time=rec["in_time"].isoformat())
    # 아직 주차 중은 아니지만 정기권인지 알려줌
    return jsonify(status="out", ss_pass=(plate in season_pass_list))



@app.post("/in_park")
def http_in_park():
    """일반 입차(자동 배정)"""
    data = request.get_json(silent=True) or {}
    plate = (data.get("plate") or "").strip()
    if not plate:
        return jsonify(detail="plate is empty"), 400
    if plate in parking:
        return jsonify(detail="already parked"), 409
    now = datetime.now()
    in_park(plate, now)
    update_park()
    return jsonify(ok=True, loca=parking[plate]["loca"], ss_pass=False)



@app.post("/in_sspark")
def http_in_sspark():
    """정기권 입차(자리 지정)"""
    data = request.get_json(silent=True) or {}
    plate = (data.get("plate") or "").strip()
    loca  = (data.get("loca") or "").strip().upper()
    join  = bool(data.get("join", False))
    if not plate:
        return jsonify(detail="plate is empty"), 400
    if plate in parking:
        return jsonify(detail="already parked"), 409
    if join and plate not in season_pass_list:
        season_pass_list.append(plate)  # 정기권 신규가입
    now = datetime.now()
    in_sspark(plate, now, loca=loca)
    if plate not in parking:
        return jsonify(detail="enter failed (invalid or occupied spot)"), 400
    update_park()
    return jsonify(ok=True, loca=parking[plate]["loca"], ss_pass=True)



@app.post("/out_park")
def http_out_park():
    """출차"""
    data = request.get_json(silent=True) or {}
    plate = (data.get("plate") or "").strip()
    if not plate:
        return jsonify(detail="plate is empty"), 400
    if plate not in parking:
        return jsonify(detail="not currently parked"), 404
    now = datetime.now()
    out_park(plate, now) 
    update_park()
    return jsonify(ok=True)



if __name__ == "__main__":
    app.run("127.0.0.1", 8000, debug=True)


