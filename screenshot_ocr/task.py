from celery import shared_task
import time
from utils.main import get_screenshot, do_ocr, get_live_result, get_final_result

@shared_task
def sleepy(duration):
    time.sleep(duration)
    return "awake now."


counter = 0
@shared_task
def start_tracking(tw_url, match_id):
    global counter
    for i in range(150):
        print(f'iteration {i} for match id {match_id}.')
        ss_url = get_screenshot(tw_url)
        print(ss_url)
        text = do_ocr(ss_url)

        if "¿CONTINUAR SERIE?" in text or "CALIFICACIONES" in text:
            print("final")
            get_final_result(text, match_id)
            break
        else:
            print("live")
            flag = get_live_result(text, match_id)
            print("flag:", flag)
            if flag == 'MATCH_END':
                counter += 1
            else:
                counter = 0

            print("counter:", counter)
            if counter >= 3:
                break

        time.sleep(2)
