import requests  

def transmit_mess(messege, rig_id): 
    #print("Сообщение на сервер", messege)
    requests.post('http://ggc.center:8000/meseger/', data = {'id_rig': rig_id, 
                                                                'messege':messege,
                                                                 })
    return()

if __name__ == '__main__':
    transmit_mess()