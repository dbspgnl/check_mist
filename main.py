import requests
import schedule
import time
import subprocess
from multiprocessing import freeze_support
import argparse

class CheckProcessor:
    def __init__(
        self,
        url: str,
        poll: int = 10,
    ) -> None:
        self.url = url
        self.poll = poll
        self.response = None
        self.offline = [True,True,True,True,True]
    
    def start(self):
        schedule.every(self.poll).seconds.do(self.check)
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    def server_status(self):
        return True if self.response.status_code == 200 else False
            
    def check(self):
        try:
            self.response = requests.get(self.url) # 주기적으로 호출한다.
            if self.server_status():
                for i in range(1,5): # 채널 1-4까지 검색 (영상 채널)
                    stream = self.response.json().get("streams")
                    if ( # 영상 스트림 on & 분석 스트림 on & 온라인 상태 = 스킵
                        not self.offline[i] and 
                        stream.get(f"mist{i}") and 
                        stream.get(f"mist{i}").get("online") == 1 and
                        ( stream.get(f"mist{i+4}") and stream.get(f"mist{i+4}").get("online") == 1 )
                    ):
                        continue
                    elif ( # 영상 스트림 on & 분석 스트림 off & 오프라인 상태 = 신규 시작 (온라인 처리)
                        self.offline[i] and 
                        stream.get(f"mist{i}") and 
                        stream.get(f"mist{i}").get("online") == 1 and
                        ( not stream.get(f"mist{i+4}") or stream.get(f"mist{i+4}").get("online") == 0 )
                    ):
                        self.offline[i] = False
                        cmd = f"mist{i}.bat"
                        process = subprocess.Popen(cmd ,shell=True)
                    elif ( # 영상 스트림 on & 분석 스트림 off & 온라인 상태 = 재시작
                        not self.offline[i] and 
                        stream.get(f"mist{i}") and 
                        stream.get(f"mist{i}").get("online") == 1 and
                        ( not stream.get(f"mist{i+4}") or stream.get(f"mist{i+4}").get("online") == 0 )
                    ):
                        self.offline[i] = True
                    elif(not stream.get(f"mist{i}")): # 영상 스트림 off = 해당 번호 오프라인으로 전환
                        self.offline[i] = True
        except Exception as e:
            print("서버 오류: "+str(e))


if __name__ == "__main__":
    freeze_support()
    parser = argparse.ArgumentParser(description="check mist online")
    parser.add_argument(
        "--url",
        required=True,
        help="check server url",
        type=str,
    )
    parser.add_argument(
        "--poll",
        required=False,
        help="polling time seconds",
        type=int,
    )
    args = parser.parse_args()
    processor = CheckProcessor(
        url=args.url,
        poll=args.poll
    )
    processor.start()