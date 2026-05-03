from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

konular = []


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
    global konular
    konular = request.form.getlist("konu")
    return redirect(url_for("yukle"))


@app.route("/yukle", methods=["GET", "POST"])
def yukle():
    if request.method == "POST":
        file = request.files["file"]
        df = pd.read_csv(file)

        sonuc = {}

        for i, konu in enumerate(konular):
            dogru = df.iloc[:, i].sum()
            toplam = len(df)
            yuzde = (dogru / toplam) * 100

            if yuzde < 50:
                durum = "Öncelikli tekrar"
                renk = "danger"
            elif yuzde < 75:
                durum = "Orta seviye tekrar"
                renk = "warning"
            else:
                durum = "İyi"
                renk = "success"

            sonuc[konu] = {
                "yuzde": round(yuzde, 2),
                "durum": durum,
                "renk": renk
            }

        en_zayif_konu = min(sonuc, key=lambda konu: sonuc[konu]["yuzde"])
        en_zayif_veri = sonuc[en_zayif_konu]

        return render_template(
            "analiz.html",
            sonuc=sonuc,
            en_zayif_konu=en_zayif_konu,
            en_zayif_veri=en_zayif_veri
        )

    return render_template("yukle.html")


if __name__ == "__main__":
    app.run(debug=True)