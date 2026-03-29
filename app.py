from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

soru_konular = {}
ogrenci_cevaplari = []
soru_sayisi = 0

@app.route("/")
def index():
    return render_template("index.html")

# SORULAR
@app.route("/sorular", methods=["GET", "POST"])
def sorular():
    global soru_konular, soru_sayisi

    if request.method == "POST":
        soru_sayisi = int(request.form.get("soru_sayisi"))
        soru_konular = {}

        for i in range(1, soru_sayisi + 1):
            konu = request.form.get(f"s{i}")
            soru_konular[i] = konu

        return redirect(url_for("index"))

    return render_template("sorular.html")

# CSV YÜKLE
@app.route("/csv_cevap", methods=["GET", "POST"])
def csv_cevap():
    global ogrenci_cevaplari

    if request.method == "POST":
        file = request.files["file"]
        df = pd.read_csv(file)

        ogrenci_cevaplari = df.values.tolist()

        # CSV kontrol
        if len(ogrenci_cevaplari[0]) != soru_sayisi:
            return "HATA: CSV soru sayısı ile sistemdeki soru sayısı uyuşmuyor!"

        return redirect(url_for("index"))

    return render_template("csv_cevap.html")

# ANALİZ
@app.route("/analiz")
def analiz():
    if not soru_konular or not ogrenci_cevaplari:
        return redirect(url_for("index"))

    konu_skor = {}

    for k in set(soru_konular.values()):
        konu_skor[k] = {"dogru": 0, "toplam": 0}

    for cevap in ogrenci_cevaplari:
        for i, c in enumerate(cevap, start=1):
            if i > soru_sayisi:
                break

            konu = soru_konular[i]
            konu_skor[konu]["toplam"] += 1

            if int(c) == 1:
                konu_skor[konu]["dogru"] += 1

    analiz_sonuc = []

    for k, v in konu_skor.items():
        oran = (v["dogru"] / v["toplam"]) * 100

        if oran < 60:
            telafi = "Konu anlatımı + temel soru çözümü"
            oncelik = 1
        elif 60 <= oran < 75:
            telafi = "Orta seviye soru çözümü"
            oncelik = 2
        else:
            telafi = "Pekiştirme / zor sorular"
            oncelik = 3

        analiz_sonuc.append({
            "konu": k,
            "oran": round(oran, 2),
            "telafi": telafi,
            "oncelik": oncelik
        })

    analiz_sonuc.sort(key=lambda x: x["oncelik"])

    return render_template("analiz.html", analiz=analiz_sonuc)


if __name__ == "__main__":
    app.run(debug=True)