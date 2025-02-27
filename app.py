from flask import Flask, render_template, request, url_for
import random
from gensim import corpora, models, similarities
from collections import defaultdict

app = Flask(__name__)

# Data Generation
patients = [f"Patient {i+1}" for i in range(100)]
symptoms = ["Fever", "Cough", "Headache", "Diarrhea", "Nausea", "Fatigue", "Abdominal pain", "Shortness of breath", "Rash", "Swelling"]
lab_tests = ["CBC", "Urinalysis", "Blood sugar", "Cholesterol", "Liver function test", "Kidney function test", "X-ray", "CT scan", "MRI", "Ultrasound"]
medications = ["Paracetamol", "Amoxicillin", "Ibuprofen", "Omeprazole", "Metformin", "Aspirin", "Cetirizine", "Lisinopril", "Atorvastatin", "Warfarin"]
effectiveness = ["Completely recovered", "Partially recovered", "No change", "Condition worsened"]

patient_records = []
for patient in patients:
    patient_symptoms = random.sample(symptoms, random.randint(1, 4))
    patient_lab_tests = random.sample(lab_tests, random.randint(1, 3))
    patient_medications = random.sample(medications, random.randint(1, 3))
    patient_effectiveness = random.choice(effectiveness)
    doctor_comment = f"{random.choice(['Condition improving', 'Condition requires further monitoring', 'Condition is critical', 'Patient is stable', 'Patient is recovering well', 'Patient is in stable condition', 'Condition is worsening', 'Further tests needed', 'Patient requires urgent care', 'Symptoms have reduced', 'Treatment is effective', 'Treatment has shown progress', 'Condition remains unchanged', 'Patient is in critical condition', 'Further observation required', 'Patient showing signs of improvement', 'Condition is under control', 'Condition fluctuating', 'Patient is responding well to treatment', 'Patient’s response to therapy is positive', 'Condition improving slowly', 'Patient is slowly gaining strength', 'Condition is stable but requires observation', 'Signs of improvement noticed', 'Patient in recovery phase', 'Patient’s health deteriorated', 'Patient under intensive care', 'Condition needs immediate attention', 'Patient not responding to current treatment', 'Condition slightly better', 'Health status improving gradually', 'Symptoms are under control', 'Patient doing better after surgery', 'Condition remains critical but stable', 'Patient requires continued care', 'Patient needs a change in medication', 'Condition has stabilized after initial treatment', 'Patient’s pain is under control', 'No significant change in condition', 'Monitoring required due to fluctuation', 'Patient showing some improvement', 'Patient’s vital signs are stable', 'Condition has plateaued', 'No signs of improvement yet', 'Condition progressing slowly but steadily', 'Condition worsening despite treatment', 'Significant improvement noted', 'Patient has been stabilized', 'Signs of recovery are visible', 'Patient is currently in recovery phase', 'Symptoms have improved dramatically', 'Treatment effectiveness continues to improve', 'Condition improving but slow', 'Patient’s recovery is on track', 'Patient condition slightly improved', 'Patient showing gradual improvement', 'Condition manageable with medication', 'No major change in condition', 'Patient’s status remains constant', 'Patient has improved significantly', 'Patient improving but requires more rest', 'Patient in critical but stable condition', 'Continued treatment necessary for recovery', 'Patient’s condition is uncertain', 'Patient is under watchful observation', 'Signs of improvement but not yet stable', 'Condition requiring long-term care', 'Patient doing better but not fully stable', 'Signs of recovery evident', 'Patient’s situation remains critical', 'Condition improving steadily', 'Stable condition with ongoing care', 'Condition slowly getting better', 'Continued monitoring recommended', 'Patient is on the road to recovery', 'Condition fluctuates between stable and critical', 'Further investigation required to determine cause', 'No immediate danger, but monitoring required', 'Condition improving with new treatment plan', 'Treatment is showing positive effects', 'Patient in good spirits, condition improving', 'Patient’s response to treatment remains positive', 'Signs of improvement but continuous observation needed', 'Patient is recovering without complications', 'Patient is showing strength in recovery', 'Condition has seen slight improvement', 'Patient’s condition remains monitored closely', 'Improvement expected over the coming days', 'Patient’s health status remains under review', 'Patient’s recovery progressing as expected', 'Condition showing positive signs', 'Recovery expected to continue', 'Patient in stable but critical phase', 'Condition remains guarded but stable', 'Condition has slightly improved', 'Further recovery expected', 'Patient requires ongoing treatment', 'Patient under observation for further changes', 'Improvement is slower than expected', 'Recovery phase in progress', 'Patient recovering with fewer complications', 'Status showing improvement over time', 'Patient showing signs of stability', 'Condition responding to treatment', 'Progressing in a stable manner', 'Improvement continues, but slow', 'Patient improving but requires constant monitoring', 'Condition improving after initial setback', 'Signs of recovery, but no major changes', 'Ongoing monitoring needed due to health status', 'Condition stable but still a concern', 'Condition slowly improving with no complications', 'Patient on track for recovery', 'Patient recovering gradually, treatment ongoing', 'Condition under steady observation', 'Condition showing slight but positive changes', 'Health improving with some setbacks', 'Condition shows signs of gradual recovery'])}"

    patient_records.append({
        "patient": patient,
        "symptoms": patient_symptoms,
        "lab_tests": patient_lab_tests,
        "medications": patient_medications,
        "effectiveness": patient_effectiveness,
        "doctor_comment": doctor_comment
    })

# Gensim Setup
gensim_data = [record["symptoms"] + record["lab_tests"] + [record["effectiveness"]] for record in patient_records]
dictionary = corpora.Dictionary(gensim_data)
corpus = [dictionary.doc2bow(data) for data in gensim_data]
tfidf = models.TfidfModel(corpus)
tfidf_corpus = tfidf[corpus]
index = similarities.MatrixSimilarity(tfidf_corpus)

# Functions
def get_medication_results(medication):
    results = []
    for record in patient_records:
        if medication in record["medications"]:
            results.append(record)
    return results

def get_disease_results(disease):
    results = []
    for record in patient_records:
        if disease in record["symptoms"]:
            results.append(record)
    return results

def get_most_effective_medications():
    medication_effectiveness = defaultdict(int)
    medication_symptoms = defaultdict(list)
    medication_lab_tests = defaultdict(list)

    for record in patient_records:
        if record["effectiveness"] == "Completely recovered":
            for medication in record["medications"]:
                medication_effectiveness[medication] += 1
                medication_symptoms[medication].extend(record["symptoms"])
                medication_lab_tests[medication].extend(record["lab_tests"])

    effective_medications = sorted(medication_effectiveness.items(), key=lambda x: x[1], reverse=True)[:5]
    results = []
    for medication, count in effective_medications:
        results.append({
            "medication": medication,
            "count": count,
            "symptoms": list(set(medication_symptoms[medication])),
            "lab_tests": list(set(medication_lab_tests[medication]))
        })
    return results

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    effective_medications = get_most_effective_medications()
    if request.method == "POST":
        medication = request.form.get("medication")
        disease = request.form.get("disease")

        if medication:
            return render_template("medication_results.html", medication=medication, records=get_medication_results(medication))
        elif disease:
            return render_template("disease_results.html", disease=disease, records=get_disease_results(disease))

    return render_template("index.html", effective_medications=effective_medications, medications=medications, diseases=symptoms)

@app.route("/medication/<medication>")
def medication_detail(medication):
    records = get_medication_results(medication)
    return render_template("medication_results.html", medication=medication, records=records)

@app.route("/disease/<disease>")
def disease_detail(disease):
    records = get_disease_results(disease)
    return render_template("disease_results.html", disease=disease, records=records)

if __name__ == "__main__":
    app.run(debug=True)