import requests  

def transmit_mess(messege, rig_id): 
	print("Сообщение на сервер", messege)
	requests.post('http://ggc.center:8000/recalibrationOff/', data = {'id_rig': id_rig, 
                                                                'messege':messege,
                                                                 })
	return()

if __name__ == '__main__':
    transmit_mess()