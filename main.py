import requests
import schedule
import time
import subprocess
from multiprocessing import freeze_support
import argparse
from ast import literal_eval

class CheckProcessor:
    def __init__(
        self,
        url: str,
        poll: int = 10,
        channel: str  = None,
    ) -> None:
        self.url = url
        self.poll = poll
        self.response = None
        self.offline = [0,0,0,0,0]
        # 채널 배열로 변환
        if channel == None: channel = "[]"
        self.channel = [i for i in literal_eval(channel)]
    
    def start(self):
        schedule.every(self.poll).seconds.do(self.check)
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    def server_status(self):
        return True if self.response.status_code == 200 else False
            
    def check(self):
        try:
            if len(self.channel) == 0: return
            self.response = requests.get(self.url) # 주기적으로 호출한다.
            if self.server_status():
                for i in range(1,5): # 채널 1-4까지 검색 (영상 채널)
                    if i+4 not in self.channel: continue # 채널 리스트에 없으면 스킵
                    stream = self.response.json().get("streams")
                    if ( # 영상 스트림 on & 분석 스트림 on & 온라인 상태 = 스킵
                        self.offline[i] > 0  and 
                        stream.get(f"mist{i}") is not None and 
                        stream.get(f"mist{i}").get("online") == 1 and
                        (stream.get(f"mist{i+4}") is not None and stream.get(f"mist{i+4}").get("online") == 1 )
                    ):
                        continue
                    elif ( # 영상 스트림 on & 분석 스트림 off & 오프라인 상태 = 신규 시작 (온라인 처리)
                        self.offline[i] == 0 and 
                        stream.get(f"mist{i}") is not None and 
                        stream.get(f"mist{i}").get("online") == 1 and
                        (stream.get(f"mist{i+4}") is None or stream.get(f"mist{i+4}").get("online") == 0 )
                    ):
                        self.offline[i] += 1
                        cmd = f"mist{i+4}.bat"
                        process = subprocess.Popen(cmd ,shell=True)
                        time.sleep(5)
                    elif(
                        stream.get(f"mist{i}") is not None or
                        (stream.get(f"mist{i}") is not None and stream.get(f"mist{i}").get("online") == 0)
                    ): # 영상 스트림 off = 해당 번호 오프라인으로 전환
                        self.offline[i] = 0
        except Exception as e:
            pass
            # print("서버 오류: "+str(e))


if __name__ == "__main__":
    freeze_support()
    parser = argparse.ArgumentParser(description="check mist online")
    parser.add_argument("--url", required=True, type=str, help="check server url")
    parser.add_argument("--poll", required=False, type=int, help="polling time seconds")
    parser.add_argument("--channel", default=None, type=str, help="Arrangement of channels to activate")
    args = parser.parse_args()
    processor = CheckProcessor(
        url=args.url,
        poll=args.poll,
        channel=args.channel
    )
    processor.start()