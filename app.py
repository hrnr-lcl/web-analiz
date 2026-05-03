from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "egitim_destek_sistemi_secret_key"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sorular", methods=["GET", "POST"])
def sorular():
    if request.method == "POST":
        soru_sayisi = int(request.form["soru_sayisi"])
        return render_template("sorular.html", soru_sayisi=soru_sayisi)

    return render_template("sorular.html", soru_sayisi=None)


@app.route("/konular_kaydet", methods=["POST"])
def konular_kaydet():
    konular = request.form.getlist("konu")
    session["konular"] = konular
    flash("Konu bilgileri başarıyla kaydedildi.", "success")
    return redirect(url_for("yukle"))


@app.route("/yukle", methods=["GET", "POST"])
def yukle():
    konular = session.get("konular", [])

    if request.method == "POST":
        if not konular:
            flash("Önce soru ve konu bilgilerini girmelisiniz.", "error")
            return redirect(url_for("sorular"))

        file = request.files.get("file")

        if not file:
            flash("Lütfen bir CSV dosyası seçiniz.", "error")
            return redirect(url_for("yukle"))

        try:
            df = pd.read_csv(file)
        except Exception:
            flash("CSV dosyası okunamadı. Lütfen doğru formatta dosya yükleyiniz.", "error")
            return redirect(url_for("yukle"))

        if df.shape[1] < len(konular):
            flash("CSV dosyasındaki sütun sayısı, girilen soru sayısından az.", "error")
            return redirect(url_for("yukle"))

        sonuc = {}

        for i, konu in enumerate(konular):
            dogru = df.iloc[:, i].sum()
            toplam = len(df)
            yuzde = (dogru / toplam) * 100 if toplam > 0 else 0

            if yuzde < 60:
                durum = "Öncelikli tekrar gerekli"
                renk = "danger"
                yorum = "Bu konuda sınıf genelinde belirgin öğrenme eksikliği vardır."
            elif yuzde < 75:
                durum = "Orta düzey tekrar gerekli"
                renk = "warning"
                yorum = "Bu konuda destekleyici tekrar çalışmaları yapılmalıdır."
            else:
                durum = "Başarılı"
                renk = "success"
                yorum = "Bu konuda sınıf genel başarısı yeterli düzeydedir."

            if konu not in sonuc:
                sonuc[konu] = {
                    "toplam_yuzde": 0,
                    "soru_sayisi": 0,
                    "durum": durum,
                    "renk": renk,
                    "yorum": yorum
                }

            sonuc[konu]["toplam_yuzde"] += yuzde
            sonuc[konu]["soru_sayisi"] += 1

        for konu, veri in sonuc.items():
            ortalama = veri["toplam_yuzde"] / veri["soru_sayisi"]
            veri["yuzde"] = round(ortalama, 2)

            if ortalama < 60:
                veri["durum"] = "Öncelikli tekrar gerekli"
                veri["renk"] = "danger"
                veri["yorum"] = "Bu konu için telafi etkinliği planlanmalıdır."
            elif ortalama < 75:
                veri["durum"] = "Orta düzey tekrar gerekli"
                veri["renk"] = "warning"
                veri["yorum"] = "Bu konuda ek alıştırma ve kısa tekrar önerilir."
            else:
                veri["durum"] = "Başarılı"
                veri["renk"] = "success"
                veri["yorum"] = "Bu konuda genel başarı yeterlidir."

            del veri["toplam_yuzde"]

        en_zayif_konu = min(sonuc, key=lambda konu: sonuc[konu]["yuzde"])
        en_guclu_konu = max(sonuc, key=lambda konu: sonuc[konu]["yuzde"])
        genel_ortalama = round(
            sum(veri["yuzde"] for veri in sonuc.values()) / len(sonuc), 2
        )

        grafik_konular = list(sonuc.keys())
        grafik_yuzdeler = [veri["yuzde"] for veri in sonuc.values()]

        return render_template(
            "analiz.html",
            sonuc=sonuc,
            en_zayif_konu=en_zayif_konu,
            en_guclu_konu=en_guclu_konu,
            genel_ortalama=genel_ortalama,
            grafik_konular=grafik_konular,
            grafik_yuzdeler=grafik_yuzdeler
        )

    return render_template("yukle.html")


@app.route("/analiz")
def analiz_bos():
    flash("Analiz görmek için önce CSV dosyası yüklemelisiniz.", "error")
    return redirect(url_for("yukle"))


if __name__ == "__main__":
    app.run(debug=True)