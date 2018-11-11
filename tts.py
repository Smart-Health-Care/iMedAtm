# coding=utf-8
import requests
import subprocess


def english(query, file):
    url = "https://translate.google.com/translate_tts"
    querystring = {"ie": "UTF-8", "client": "tw-ob",
                   "q": query,
                   "tl": "en", "total": "1", "idx": "0", "textlen": str(query.__len__())}

    headers = {
        'Cache-Control': "no-cache",
        'Postman-Token': "d66ad556-a182-4d59-63cc-66cff5cfbf23"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    f = open("audio/" + file, "w")
    f.write(response.content)
    f.close()


def hindi(query, file):
    url = "https://translate.google.com/translate_tts"

    querystring = {"ie": "UTF-8", "client": "tw-ob", "q": query, "tl": "hi",
                   "total": "1", "idx": "0", "textlen": str(query.__len__())}

    headers = {
        'Cache-Control': "no-cache",
        'Postman-Token': "f33e4e20-c050-6f73-2a49-1c7e97b142ef"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    f = open("audio/" + file, "w")
    f.write(response.content)
    f.close()


def tamil(query, file):
    url = "https://translate.google.com/translate_tts"

    querystring = {"ie": "UTF-8", "client": "tw-ob", "q": query, "tl": "ta",
                   "total": "1", "idx": "0", "textlen": str(query.__len__())}

    headers = {
        'Cache-Control': "no-cache",
        'Postman-Token': "f33e4e20-c050-6f73-2a49-1c7e97b142ef"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    f = open("audio/" + file, "w")
    f.write(response.content)
    f.close()


def fetch():
    intro_e = "If you want to buy your prescribed medicines, please scan your aadhar's QR,  or else select common drugs"
    intro_h = "यदि आप अपनी निर्धारित दवाएं खरीदना चाहते हैं, तो कृपया अपने आधार के क्यूआर को स्कैन करें, या फिर सामान्य दवाओं का चयन करें"

    english(intro_e, "Intro.wav")
    hindi(intro_h, "IntroH.wav")

    show_qr = "Please show your aadhar's qr in front of the camera"
    show_qr_h = "कृपया कैमरे के सामने अपना आधार का क्यूआर दिखाएं"

    english(show_qr, "showQR.wav")
    hindi(show_qr_h, "showQRH.wav")

    otp = "Please enter the one time password sent to your mobile phone"
    otp_h = "कृपया अपने मोबाइल फोन पर भेजे गए एक बार पासवर्ड दर्ज करें"

    english(otp, "OTP.wav")
    hindi(otp_h, "OTPH.wav")

    prescription_list = "please Select the required prescription to dispense"
    prescription_list_h = "कृपया वितरण के लिए आवश्यक पर्चे का चयन करें"

    english(prescription_list, "prescriptionList.wav")
    hindi(prescription_list_h, "prescriptionListH.wav")

    prescription_view = "Change the amount of medicines if necessary or click submit to dispense the prescribed drugs"
    prescription_view_h = "यदि आवश्यक हो तो दवाइयों की मात्रा बदलें या निर्धारित दवाओं को बांटने के लिए सबमिट पर क्लिक करें"

    english(prescription_view, "PrescriptionView.wav")
    hindi(prescription_view_h, "PrescriptionViewH.wav")

    mobile_view = "Enter your phone number to process payment"
    mobile_view_h = "भुगतान संसाधित करने के लिए अपना फोन नंबर दर्ज करें"

    english(mobile_view, "mobile.wav")
    hindi(mobile_view_h, "mobileH.wav")

    medicine_dispensed = "Medicine Dispensed"
    med_disp_h = "चिकित्सा निराश"

    english(medicine_dispensed, "medDisp.wav")
    hindi(med_disp_h, "medDispH.wav")

    presp_print = "Do you want a printed prescription, press yes or no"
    presp_print_h = "क्या आप एक मुद्रित पर्चे चाहते हैं, हाँ या नहीं दबाएं"

    english(presp_print, "PrespPrint.wav")
    hindi(presp_print_h, "PrespPrintH.wav")

    thankyou = "Thank you for using iMed Dispenser, get well soon"
    thankyou_h = "IMed डिस्पेंसर का उपयोग करने के लिए धन्यवाद, जल्द ही ठीक हो जाओ"

    english(thankyou, "Thank.wav")
    hindi(thankyou_h, "ThankH.wav")

    pos = "Please touch on the medicine you need, as many times as necessary and click bill to dispense"
    pos_h = "जकृपया जितनी बार आवश्यक हो उतनी दवा पर स्पर्श करें और वितरण के लिए बिल पर क्लिक करें"

    english(pos, "POS.wav")
    hindi(pos_h, "POSH.wav")

    bill = "click bill, to bill"
    bill_h = "बिल करने के लिए बिल पर क्लिक करें"

    english(bill, "bill.wav")
    hindi(bill_h, "billH.wav")

    payment = "Do you want to confirm the payment of 1 bandage, for 10 ruppees"
    payment_h = "क्या आप 10 रुपये के लिए 5 पट्टियों के भुगतान की पुष्टि करना चाहते हैं"

    english(payment, "Payment.wav")
    hindi(payment_h, "PaymentH.wav")

    intro = "Click this icon for voice instructions"
    intro_h = "ध्वनि निर्देशों के लिए इस आइकन पर क्लिक करें"

    english(intro, "intro.wav")
    hindi(intro_h, "introH.wav")


def pos_tts(qty):
    temp_file = 'english.wav'
    temp_file_h = 'hindi.wav'
    payment = "Do you want to confirm the payment of " + str(qty) + " bandages, for " + str(qty * 10) + " ruppees?"
    payment_h = "क्या आप " + str(qty * 10) + " रुपये के लिए " + str(
        qty) + " पट्टियों के भुगतान की पुष्टि करना चाहते हैं?"
    hindi(payment_h, temp_file_h)
    english(payment, temp_file)
    process = subprocess.Popen(['mpg123', "/home/pi/iMedDispenser/iMedAtm/audio/" + temp_file_h])
