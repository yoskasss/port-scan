import socket
import threading
import sys

# Kullanıcıdan hedef IP adresini alır
ip = input("Hedef ip adresi : ")

# Zaman aşımı süresi; bağlantı işlemleri bu süre sonunda başarısız olursa kapalı olarak kabul edilecek
timeout = 0.2

# Açık portları saklamak için bir liste; başarılı bağlantılar bu listeye eklenecek
acik_portlar = []

# En son taranan kapalı portu kaydetmek için bir değişken
kapali_port = 0

# Ekrana yazma işlemlerinde çakışmaları önlemek için bir kilit (Lock) oluşturur
print_lock = threading.Lock()

# Port tarama işlevi
def port_tara(port):
    global kapali_port
    try:
        # Yeni bir TCP soketi oluşturur
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Soket bağlantısı için zaman aşımını ayarlar
            s.settimeout(timeout)
            
            # Hedef IP adresindeki belirli bir porta bağlantı kurmayı dener
            # Eğer bağlantı kurulursa, 0 döndürerek açıldığını belirtir
            if s.connect_ex((ip, port)) == 0:
                # Ekrana aynı anda yazmayı önlemek için kilit kullanır
                with print_lock:
                    # Açık portları listeye ekler
                    acik_portlar.append(port)
                    # Portun açık olduğunu ekrana yazar
                    print(f"{port} Açık")
            else:
                # Eğer bağlantı kurulamazsa portu kapalı olarak işaretler
                with print_lock:
                    kapali_port = port
                    # Kapalı port bilgisini en üstte güncellemek için ekrana yazar
                    sys.stdout.write(f"\r{kapali_port} Kapalı")
                    sys.stdout.flush()  # Ekranı güncellemek için çıktıyı hemen ekrana yansıtır
    except:
        pass  # Hata durumunda işlemi geçer, ekrana hata yazmaz

# Port aralığını belirler; burada 1'den 65535'e kadar tüm portları tarayacağız
port_araligi = range(1, 65535)

# Tüm iş parçacıklarını saklamak için bir liste
threads = []

# Her port için bir iş parçacığı oluşturup başlatır
for port in port_araligi:
    # Yeni bir iş parçacığı oluşturur ve `port_tara` işlevini belirli bir portla çalıştırır
    thread = threading.Thread(target=port_tara, args=(port,))
    threads.append(thread)  # İş parçacığını listeye ekler
    thread.start()  # İş parçacığını başlatır
    
    # Aynı anda çalışan iş parçacığı sayısını sınırlamak için 500 iş parçacığına ulaşıldığında bekler
    if len(threads) >= 500:
        # Tüm aktif iş parçacıklarının tamamlanmasını bekler
        for t in threads:
            t.join()
        # İş parçacığı listesi temizlenir, böylece yeni iş parçacıklarıyla devam edebiliriz
        threads = []

# Kalan tüm iş parçacıklarının bitmesini bekler
for t in threads:
    t.join()

# Tüm açık portları ekrana yazdırır
print("\nAçık Portlar:", acik_portlar)
