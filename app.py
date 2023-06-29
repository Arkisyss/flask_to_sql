from flask import Flask, render_template, request, url_for
import re
import bleach
import pymysql

# création de l'application
app = Flask(__name__)

# configuration des données de la db
db_config = {
    'user' : 'root',
    'password' : 'root',
    'host' : '127.0.0.1',
    'database' : 'flaskdb'
}

# créé une route pour accéder à mon serveur temp et accéder à la page "Home"
@app.route('/') 
def home():
    return render_template('index.html')
    
# Créé la route de la page de validation
@app.route('/retour', methods=['POST']) 

# Création de la fonction principale 
# Définition de la fonction de validation des données du formulaire, vérifaction des données, protection des données ainsi que renvoie vers la page de feedback.
def form_valide():
    
    # Fonction auxiliaire pour valider l'adresse email
    def email_valide(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email)
    
    # attribution des fonctions
    # empecher les scripts
    nom = bleach.clean(request.form.get('nom'))
    prenom = bleach.clean(request.form.get('prenom'))
    email = bleach.clean(request.form.get('email'))
    pays = bleach.clean(request.form.get('pays'))
    genre = bleach.clean(request.form.get('genre'))
    message = bleach.clean(request.form.get('message'))
    sujets = request.form.getlist('sujets')  # Utilisez getlist() pour récupérer une liste de valeurs
    honeypot = request.form.get('honeypot')  # Champ honeypot
      
    # Vérification des caractères dans "nom" et "prenom"
    if not re.match(r'^[A-Za-zÀ-ÿ\s-]+$', nom) or not re.match(r'^[A-Za-zÀ-ÿ\s-]+$', prenom):
        return "Le nom et le prénom doivent contenir uniquement des lettres et/ou être rempli."

    # Vérification de l'adresse email
    if not email_valide(email):
        return "Veuillez indiquer une adresse mail valide"

    # Vérification des champs obligatoires (nom, prenom, email, pays, genre, message)
    if not nom or not prenom or not email or not pays or not genre or not message:
        return "Veuillez remplir tous les champs du formulaire."
    
    # Faire en sorte que si aucun sujet n'est sélectionné alors le choix par défaut est "Autre"
    if not sujets:
        sujets = ["Autre"]
    
    # Vérification honeypot antispam
    if honeypot:
        return "Êtes-vous un robot ?"
    
    # Appel de la fonction insert_data pour insérer les données dans la db
    insert_data(nom, prenom, email, pays, genre, message, sujets)
    
    # renvoyé toutes les infos entré sur la page retour.html pour avoir un feedback.
    return render_template('retour.html', prenom = prenom, nom = nom, email = email, pays = pays, genre = genre, message = message, sujets = sujets )
 
 # fonctions qui va insérer les données, les changer et dans la db
def insert_data(nom, prenom, email, pays, genre, message, sujets):
    connexion = pymysql.connect(host='127.0.0.1', user='root', 
                                password='root', database='flaskdb')
    
    # créér un cursor pour exécuter les requètes SQL
    cursor = connexion.cursor()
    
    # Défini la requête d'insertion avec des paramètres (%s) pour les valeurs à insérer
    query = "INSERT INTO info_user (nom, prenom, email, pays, genre, message, sujets) VALUES (%s, %s, %s, %s, %s, %s, %s)"

    # Exécute la requête en fournissant les valeurs à insérer dans le tuple
    cursor.execute(query, (nom, prenom, email, pays, genre, message, ','.join(sujets)))
    
    # valide les changements de db
    connexion.commit()
    
    #ferme le cursor et la connexion
    cursor.close()
    connexion.close()

# fonctions de création de tables pour la db
def create_info_user_table():
    connect = pymysql.connect(**db_config)
    cursor = connect.cursor()

    # Création de la table "info_user" sur mariadb
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS info_user (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nom VARCHAR(20) NOT NULL,
            prenom VARCHAR(20) NOT NULL,
            email VARCHAR(50) NOT NULL,
            pays VARCHAR(50) NOT NULL,
            genre VARCHAR(10) NOT NULL,
            message TEXT NOT NULL,
            sujets TEXT NOT NULL
        )
    """)

    connect.commit()
    connect.close()

create_info_user_table()

# Lancement de l'app via le terminal
if __name__ == "__main__":
    app.run()
