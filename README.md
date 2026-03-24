# Architektúra
Az alábbi komponensek, mint microservice-ek fognak futni a kész keretrendszerben:
-	Deployment: Docker
    o	Korábbi tapasztalat, kezelhetőség, alkalmazás image-ek tárolása Docker Hub-on
-	CICD: GitHub Actions
    o	A CICD pipleine a következő lesz:
        -	Build: kódfeltöltés után statikus kódvalidáció, Unit tesztek a funkcionalitás tesztelésére (pl: OCR helyesen fut-e)
        -	Deployment: sikeres build után közzétesszük az új alkalmazást Docker Hub-on, amit aztán behúz a keretrendszer
-	Frontend: NodeJS
    o	Webszerver fejlesztésére elterjedt, korábbi tapasztalat
-	Adattárolás: MinIO
    o	Képekre, videókra van tervezve, jól skálázható és gyarkan használt ML-ekkel, ha összetettebb megoldást szeretnénk az OCR megvalósítására
-	Adattovábbítás: Redis (Redis Queue)
    o	Könnyen implelentálható, in-cache üzenet bróker
-	További eszközök/csomagok:
    o	kubectl (klaszterkezelés vezérlőfelülete)
    o	helm (yaml konfigurációs file-ok paraméterezése szükség esetén, mint laboron)
