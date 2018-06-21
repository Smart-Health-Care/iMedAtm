import requests
from prettytable import PrettyTable
import cups
from iMedAtm.settings import SERVER_URL


def print_prescription(prescription_id):
    response = requests.get(SERVER_URL + "/api/v1/prescription_details?id=" + str(prescription_id))
    fileName = "imed.txt"
    if response.status_code == 200:
        headers = ["Medicine", "B", "L", "D", "Aft", "Bfr"]
        t = PrettyTable(headers)
        data = response.json()
        for id, medicine in enumerate(data.get("data")):
            t.add_row([medicine.get("medicine").strip(), medicine.get("B"), medicine.get("L"),
                       medicine.get("D"), medicine.get("Aft"), medicine.get("Bfr")])
        f = open(fileName, "w")
        f.write("\t\t iMed Dispenser\n")
        f.write("Doctor Name: " + data.get("doctor") + "\n")
        f.write("Patient Name: " + data.get("patient_name") + "\n")
        f.write("Patient Aadhar Number: " + str(data.get("aadhar_number")) + "\n")
        f.write("Date: " + data.get("date") + "\n")
        f.write(str(t))
        f.write("\n\nB - Breakfast\n"
                "L - Lunch\n"
                "D - Dinner\n"
                "Aft - After Food\n"
                "Bfr - Before Food\n")
        f.close()
        conn = cups.Connection()
        printers = conn.getPrinters()
        printer_name = printers.keys()[0]
        conn.printFile(printer_name, fileName, " ",
                       {"cpi": "23", "lpi": "10", "fit-to-page": "True"})
