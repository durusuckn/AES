import socket, threading#kütüphaneler içe aktarılır

connections = [] #bağlantılar listesi

def handle_user_connection(connection: socket.socket, address: str) -> None: #https://docs.python.org/3/library/typing.html
    while True:#sonsuz döngü açılarak kullanıcılardan gelen mesajlar alınır
        try:
            msg = connection.recv(1024) #mesaj alınır

            if msg:#eğer mesaj alınmışsa

                print(f'{address[0]}:{address[1]} - {msg.decode()}')#mesajın hangi client tarafından gönderildiği
                # ve encrypt edilmiş mesajı print edilir

                broadcast(msg, connection)#broadcast işlevi çağrılır aşağıda işlevini anlatacağım

            else: #eğer mesaj alınamadıysa
                remove_connection(connection)#ilgili clientin bağlantısı kesilir
                break#döngü durdurulur

        except Exception as e:#herhangi bir sorunda
            print(f'Error to handle user connection: {e}')#hata mesajı verilir
            remove_connection(connection)#ilgili clientin bağlantısı kesilir
            break#döngü kapatılır


def broadcast(message: str, connection: socket.socket) -> None:
    #temel olarak bütün clientlere gelen mesajı iletir(mesajı gönderen client hariç)

    for client_conn in connections:#liste içerisinde teker teker dolaşılır
        if client_conn != connection:#eğer ip mesajı gönderen clientin ip'si değilse
            try:
                client_conn.send(message)#mesaj gönderilir
            except Exception as e:#hata anında
                print('Error broadcasting message: {e}')#hata mesajı print edilir
                remove_connection(client_conn)#ilgili client bağlantısı sonlandırılır
#remove_connection işlevini aşağıda açıklıyorum

def remove_connection(conn: socket.socket) -> None:
    #temelde ilgili clientin bağlantısını sonladırır

    if conn in connections:#eğer connections listesindeki herhangi bir ip ile eşleşiyorsa
        conn.close()#bağlantı kapatılır
        connections.remove(conn)#ilgili client listeden silinir


def server() -> None:

    LISTENING_PORT = 12000#serverin hangi port üzerinde çalışacağını belirleriz

    try:
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#soket bağlantısı AF_INET(ipv4 protokolu)/SOCK_STREAM(tcp) ile açılır
        socket_instance.bind(('', LISTENING_PORT))#bağlantılar beklenir
        socket_instance.listen(3)#bu servera ne kadar client bağlanabileceğinin sayısı listen fonksiyonu ile belirlenir

        print('Server running!')

        while True:#sonsuz döngü

            socket_connection, address = socket_instance.accept()#gelen bağlantılar kabul edilir
            connections.append(socket_connection)#bağlantı listeye atılır
            threading.Thread(target=handle_user_connection, args=[socket_connection, address]).start()
            #thread yapısı kullanmamızın sebebi herhangi bir anda servera bir bağlantı isteği gelebilir veya mesaj gelebilir
            #eğer bu işlemleri thread kullanmadan yaparsak verimli bir uygulama elde edemeyiz
            #her bir client için bir iş parçacığı oluşturulur bu da karışıklığı engeller

    except Exception as e:
        print(f'An error has occurred when instancing socket: {e}')
    finally:
        # In case of any problem we clean all connections and close the server connection
        if len(connections) > 0:#eğer connections listesinde hala bağlantı varsa
            for conn in connections:
                remove_connection(conn)#bütün bağlantılar kapatılır

        socket_instance.close()#soket bağlantısı kapatılır



server()#server fonksiyonu başlatılır