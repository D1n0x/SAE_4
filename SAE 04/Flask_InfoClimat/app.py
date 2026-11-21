#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, flash

app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'

                                    ## à ajouter
from flask import session, g
import pymysql.cursors

def get_db():
    if 'db' not in g:
        g.db =  pymysql.connect(
            host="localhost",                 # à modifier
            user="login",                     # à modifier
            password="secret",                # à modifier
            database="BDD_s1_tp",             # à modifier
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


#======================VILLE==========
@app.route('/ville/show')
def show_ville():
    mycursor = get_db().cursor()
    sql = ''' SELECT id_ville, nom_ville, code_postal
    FROM ville
    ORDER BY nom_ville;'''
    mycursor.execute(sql)
    villes = mycursor.fetchall()
    return render_template('ville/show_ville.html', villes=villes)

@app.route('/ville/add', methods=['GET'])
def add_ville():
    print('''affichage du formulaire pour ajouter une ville''')
    return render_template('ville/add_ville.html')

@app.route('/ville/add', methods=['POST'])
def valid_add_ville():
    print('''ajout de la ville''')
    nom_ville = request.form.get('nom_ville')
    code_postal = request.form.get('code_postal')
    mycursor = get_db().cursor()
    tuple_param = (nom_ville, code_postal)
    sql = "INSERT INTO ville(id_ville, nom_ville, code_postal) VALUES (NULL, %s, %s);"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/ville/show')

@app.route('/ville/edit', methods=['GET'])
def edit_ville():
    print('''affichage du formulaire pour modifier une ville''')
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_ville, nom_ville, code_postal
    FROM ville
    WHERE id_ville=%s;'''
    tuple_param = (id,)
    mycursor.execute(sql, tuple_param)
    ville = mycursor.fetchone()
    return render_template('ville/edit_ville.html', ville=ville)

@app.route('/ville/edit', methods=['POST'])
def valid_edit_ville():
    print('''modification de la ville''')
    id = request.form.get('id')
    nom_ville = request.form.get('nom_ville')
    code_postal = request.form.get('code_postal')
    mycursor = get_db().cursor()
    tuple_param = (nom_ville, code_postal, id)
    sql = "UPDATE ville SET nom_ville = %s, code_postal = %s WHERE id_ville=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/ville/show')

@app.route('/ville/delete')
def delete_ville():
    print('''suppression d'une ville''')
    id = request.args.get('id', 0)
    mycursor = get_db().cursor()
    tuple_param = (id,)
    sql = "DELETE FROM se_situer WHERE ville_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM ville WHERE id_ville=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/ville/show')


#=======================ADRESSE (+ se_situer)======================
@app.route('/adresse/show')
def show_adresse():
    mycursor = get_db().cursor()
    sql = ''' SELECT adresse.id_adresse, adresse.nom_rue, adresse.numero_rue,
    ville.nom_ville, ville.code_postal
    FROM adresse
    LEFT JOIN se_situer ON adresse.id_adresse = se_situer.adresse_id
    LEFT JOIN ville ON se_situer.ville_id = ville.id_ville
    ORDER BY adresse.nom_rue;'''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()
    return render_template('adresse/show_adresse.html', adresses=adresses)

@app.route('/adresse/add', methods=['GET'])
def add_adresse():
    print('''affichage du formulaire pour ajouter une adresse''')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_ville, nom_ville FROM ville ORDER BY nom_ville;'''
    mycursor.execute(sql)
    villes = mycursor.fetchall()
    return render_template('adresse/add_adresse.html', villes=villes)

@app.route('/adresse/add', methods=['POST'])
def valid_add_adresse():
    print('''ajout de l'adresse''')
    nom_rue = request.form.get('nom_rue')
    numero_rue = request.form.get('numero_rue')
    id_ville = request.form.get('id_ville')
    mycursor = get_db().cursor()
    tuple_param = (nom_rue, numero_rue)
    sql = "INSERT INTO adresse(id_adresse, nom_rue, numero_rue) VALUES (NULL, %s, %s);"
    mycursor.execute(sql, tuple_param)
    tuple_param = (id_ville,)
    sql = "INSERT INTO se_situer(adresse_id, ville_id) VALUES (LAST_INSERT_ID(), %s);"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/adresse/show')

@app.route('/adresse/edit', methods=['GET'])
def edit_adresse():
    print('''affichage du formulaire pour modifier une adresse''')
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = ''' SELECT adresse.id_adresse, adresse.nom_rue, adresse.numero_rue, se_situer.ville_id
    FROM adresse
    LEFT JOIN se_situer ON adresse.id_adresse = se_situer.adresse_id
    WHERE adresse.id_adresse=%s;'''
    tuple_param = (id,)
    mycursor.execute(sql, tuple_param)
    adresse = mycursor.fetchone()
    sql = ''' SELECT id_ville, nom_ville FROM ville ORDER BY nom_ville;'''
    mycursor.execute(sql)
    villes = mycursor.fetchall()
    return render_template('adresse/edit_adresse.html', adresse=adresse, villes=villes)

@app.route('/adresse/edit', methods=['POST'])
def valid_edit_adresse():
    print('''modification de l'adresse''')
    id = request.form.get('id')
    nom_rue = request.form.get('nom_rue')
    numero_rue = request.form.get('numero_rue')
    id_ville = request.form.get('id_ville')
    mycursor = get_db().cursor()
    tuple_param = (nom_rue, numero_rue, id)
    sql = "UPDATE adresse SET nom_rue = %s, numero_rue = %s WHERE id_adresse=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM se_situer WHERE adresse_id=%s;"
    mycursor.execute(sql, (id,))
    sql = "INSERT INTO se_situer(adresse_id, ville_id) VALUES (%s, %s);"
    mycursor.execute(sql, (id, id_ville))
    get_db().commit()
    return redirect('/adresse/show')

@app.route('/adresse/delete')
def delete_adresse():
    print('''suppression d'une adresse''')
    id = request.args.get('id', 0)
    mycursor = get_db().cursor()
    tuple_param = (id,)
    sql = "DELETE FROM se_situer WHERE adresse_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM adresse WHERE id_adresse=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/adresse/show')


#==============FORMATEUR==============================
@app.route('/formateur/show')
def show_formateur():
    mycursor = get_db().cursor()
    sql = ''' SELECT id_formateur, nom_formateur, prenom_formateur
    FROM formateur
    ORDER BY nom_formateur;'''
    mycursor.execute(sql)
    formateurs = mycursor.fetchall()
    return render_template('formateur/show_formateur.html', formateurs=formateurs)

@app.route('/formateur/add', methods=['GET'])
def add_formateur():
    print('''affichage du formulaire pour ajouter un formateur''')
    return render_template('formateur/add_formateur.html')

@app.route('/formateur/add', methods=['POST'])
def valid_add_formateur():
    print('''ajout du formateur''')
    nom_formateur = request.form.get('nom_formateur')
    prenom_formateur = request.form.get('prenom_formateur')
    mycursor = get_db().cursor()
    tuple_param = (nom_formateur, prenom_formateur)
    sql = "INSERT INTO formateur(id_formateur, nom_formateur, prenom_formateur) VALUES (NULL, %s, %s);"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/formateur/show')

@app.route('/formateur/edit', methods=['GET'])
def edit_formateur():
    print('''affichage du formulaire pour modifier un formateur''')
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_formateur, nom_formateur, prenom_formateur
    FROM formateur
    WHERE id_formateur=%s;'''
    tuple_param = (id,)
    mycursor.execute(sql, tuple_param)
    formateur = mycursor.fetchone()
    return render_template('formateur/edit_formateur.html', formateur=formateur)

@app.route('/formateur/edit', methods=['POST'])
def valid_edit_formateur():
    print('''modification du formateur''')
    id = request.form.get('id')
    nom_formateur = request.form.get('nom_formateur')
    prenom_formateur = request.form.get('prenom_formateur')
    mycursor = get_db().cursor()
    tuple_param = (nom_formateur, prenom_formateur, id)
    sql = "UPDATE formateur SET nom_formateur = %s, prenom_formateur = %s WHERE id_formateur=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/formateur/show')

@app.route('/formateur/delete')
def delete_formateur():
    print('''suppression d'un formateur''')
    id = request.args.get('id', 0)
    mycursor = get_db().cursor()
    tuple_param = (id,)
    sql = "DELETE FROM former WHERE formateur_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM formateur WHERE id_formateur=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/formateur/show')


#====PROFESSION===========
def show_profession():
    mycursor = get_db().cursor()
    sql = ''' SELECT id_profession, nom_profession
    FROM profession
    ORDER BY nom_profession;'''
    mycursor.execute(sql)
    professions = mycursor.fetchall()
    return render_template('profession/show_profession.html', professions=professions)

@app.route('/profession/add', methods=['GET'])
def add_profession():
    print('''affichage du formulaire pour ajouter une profession''')
    return render_template('profession/add_profession.html')

@app.route('/profession/add', methods=['POST'])
def valid_add_profession():
    print('''ajout de la profession''')
    nom_profession = request.form.get('nom_profession')
    mycursor = get_db().cursor()
    tuple_param = (nom_profession,)
    sql = "INSERT INTO profession(id_profession, nom_profession) VALUES (NULL, %s);"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/profession/show')

@app.route('/profession/edit', methods=['GET'])
def edit_profession():
    print('''affichage du formulaire pour modifier une profession''')
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_profession, nom_profession
    FROM profession
    WHERE id_profession=%s;'''
    tuple_param = (id,)
    mycursor.execute(sql, tuple_param)
    profession = mycursor.fetchone()
    return render_template('profession/edit_profession.html', profession=profession)

@app.route('/profession/edit', methods=['POST'])
def valid_edit_profession():
    print('''modification de la profession''')
    id = request.form.get('id')
    nom_profession = request.form.get('nom_profession')
    mycursor = get_db().cursor()
    tuple_param = (nom_profession, id)
    sql = "UPDATE profession SET nom_profession = %s WHERE id_profession=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/profession/show')

@app.route('/profession/delete')
def delete_profession():
    print('''suppression d'une profession''')
    id = request.args.get('id', 0)
    mycursor = get_db().cursor()
    tuple_param = (id,)
    sql = "DELETE FROM travailler WHERE profession_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM profession WHERE id_profession=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/profession/show')


#==============ATELIER=================
@app.route('/atelier/show')
def show_atelier():
    mycursor = get_db().cursor()
    sql = ''' SELECT id_atelier, nom_atelier, theme_atelier
    FROM atelier
    ORDER BY nom_atelier;'''
    mycursor.execute(sql)
    ateliers = mycursor.fetchall()
    return render_template('atelier/show_atelier.html', ateliers=ateliers)

@app.route('/atelier/add', methods=['GET'])
def add_atelier():
    print('''affichage du formulaire pour ajouter un atelier''')
    return render_template('atelier/add_atelier.html')

@app.route('/atelier/add', methods=['POST'])
def valid_add_atelier():
    print('''ajout de l'atelier''')
    nom_atelier = request.form.get('nom_atelier')
    theme_atelier = request.form.get('theme_atelier')
    mycursor = get_db().cursor()
    tuple_param = (nom_atelier, theme_atelier)
    sql = "INSERT INTO atelier(id_atelier, nom_atelier, theme_atelier) VALUES (NULL, %s, %s);"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/atelier/show')

@app.route('/atelier/edit', methods=['GET'])
def edit_atelier():
    print('''affichage du formulaire pour modifier un atelier''')
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_atelier, nom_atelier, theme_atelier
    FROM atelier
    WHERE id_atelier=%s;'''
    tuple_param = (id,)
    mycursor.execute(sql, tuple_param)
    atelier = mycursor.fetchone()
    return render_template('atelier/edit_atelier.html', atelier=atelier)

@app.route('/atelier/edit', methods=['POST'])
def valid_edit_atelier():
    print('''modification de l'atelier''')
    id = request.form.get('id')
    nom_atelier = request.form.get('nom_atelier')
    theme_atelier = request.form.get('theme_atelier')
    mycursor = get_db().cursor()
    tuple_param = (nom_atelier, theme_atelier, id)
    sql = "UPDATE atelier SET nom_atelier = %s, theme_atelier = %s WHERE id_atelier=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/atelier/show')

@app.route('/atelier/delete')
def delete_atelier():
    print('''suppression d'un atelier''')
    id = request.args.get('id', 0)
    mycursor = get_db().cursor()
    tuple_param = (id,)
    sql = "DELETE FROM s_occuper WHERE atelier_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM atelier WHERE id_atelier=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/atelier/show')


#==============ANIMATEUR=================
@app.route('/')
@app.route('/animateur/show')
def show_animateur():
    mycursor = get_db().cursor()
    sql = ''' SELECT animateur.id_animateur, animateur.nom_animateur, animateur.prenom_animateur,
    animateur.telephone_animateur, animateur.disponibilite,
    adresse.nom_rue, adresse.numero_rue
    FROM animateur
    JOIN adresse ON animateur.id_adresse = adresse.id_adresse
    ORDER BY animateur.nom_animateur;'''
    mycursor.execute(sql)
    animateurs = mycursor.fetchall()
    return render_template('animateur/show_animateur.html', animateurs=animateurs)

@app.route('/animateur/add', methods=['GET'])
def add_animateur():
    print('''affichage du formulaire pour ajouter un animateur''')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_adresse, nom_rue, numero_rue FROM adresse ORDER BY nom_rue;'''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()
    return render_template('animateur/add_animateur.html', adresses=adresses)

@app.route('/animateur/add', methods=['POST'])
def valid_add_animateur():
    print('''ajout de l'animateur''')
    nom_animateur = request.form.get('nom_animateur')
    prenom_animateur = request.form.get('prenom_animateur')
    telephone_animateur = request.form.get('telephone_animateur')
    disponibilite = request.form.get('disponibilite', 0)
    id_adresse = request.form.get('id_adresse')
    mycursor = get_db().cursor()
    tuple_param = (nom_animateur, prenom_animateur, telephone_animateur, disponibilite, id_adresse)
    sql = '''INSERT INTO animateur(id_animateur, nom_animateur, prenom_animateur, telephone_animateur, disponibilite, id_adresse)
    VALUES (NULL, %s, %s, %s, %s, %s);'''
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/animateur/show')

@app.route('/animateur/edit', methods=['GET'])
def edit_animateur():
    print('''affichage du formulaire pour modifier un animateur''')
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_animateur, nom_animateur, prenom_animateur, telephone_animateur, disponibilite, id_adresse
    FROM animateur
    WHERE id_animateur=%s;'''
    tuple_param = (id,)
    mycursor.execute(sql, tuple_param)
    animateur = mycursor.fetchone()
    sql = ''' SELECT id_adresse, nom_rue, numero_rue FROM adresse ORDER BY nom_rue;'''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()
    return render_template('animateur/edit_animateur.html', animateur=animateur, adresses=adresses)

@app.route('/animateur/edit', methods=['POST'])
def valid_edit_animateur():
    print('''modification de l'animateur''')
    id = request.form.get('id')
    nom_animateur = request.form.get('nom_animateur')
    prenom_animateur = request.form.get('prenom_animateur')
    telephone_animateur = request.form.get('telephone_animateur')
    disponibilite = request.form.get('disponibilite', 0)
    id_adresse = request.form.get('id_adresse')
    mycursor = get_db().cursor()
    tuple_param = (nom_animateur, prenom_animateur, telephone_animateur, disponibilite, id_adresse, id)
    sql = '''UPDATE animateur
    SET nom_animateur = %s, prenom_animateur = %s, telephone_animateur = %s, disponibilite = %s, id_adresse = %s
    WHERE id_animateur=%s;'''
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/animateur/show')

@app.route('/animateur/delete')
def delete_animateur():
    print('''suppression d'un animateur''')
    id = request.args.get('id', 0)
    mycursor = get_db().cursor()
    tuple_param = (id,)
    sql = "DELETE FROM animer WHERE animateur_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM s_occuper WHERE animateur_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM former WHERE animateur_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM travailler WHERE animateur_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM animateur WHERE id_animateur=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/animateur/show')


#====================ANIMATION===========
@app.route('/animation/show')
def show_animation():
    mycursor = get_db().cursor()
    sql = ''' SELECT animation.id_animation, animation.nom_animation, animation.nb_places_disponibles,
    animation.date_animation, atelier.nom_atelier, adresse.nom_rue, adresse.numero_rue
    FROM animation
    JOIN atelier ON animation.id_atelier = atelier.id_atelier
    JOIN adresse ON animation.id_adresse = adresse.id_adresse
    ORDER BY animation.date_animation;'''
    mycursor.execute(sql)
    animations = mycursor.fetchall()
    return render_template('animation/show_animation.html', animations=animations)

@app.route('/animation/add', methods=['GET'])
def add_animation():
    print('''affichage du formulaire pour ajouter une animation''')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_atelier, nom_atelier FROM atelier ORDER BY nom_atelier;'''
    mycursor.execute(sql)
    ateliers = mycursor.fetchall()
    sql = ''' SELECT id_adresse, nom_rue, numero_rue FROM adresse ORDER BY nom_rue;'''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()
    return render_template('animation/add_animation.html', ateliers=ateliers, adresses=adresses)

@app.route('/animation/add', methods=['POST'])
def valid_add_animation():
    print('''ajout de l'animation''')
    nom_animation = request.form.get('nom_animation')
    nb_places_disponibles = request.form.get('nb_places_disponibles')
    date_animation = request.form.get('date_animation')
    id_atelier = request.form.get('id_atelier')
    id_adresse = request.form.get('id_adresse')
    mycursor = get_db().cursor()
    tuple_param = (nom_animation, nb_places_disponibles, date_animation, id_atelier, id_adresse)
    sql = '''INSERT INTO animation(id_animation, nom_animation, nb_places_disponibles, date_animation, id_atelier, id_adresse)
    VALUES (NULL, %s, %s, %s, %s, %s);'''
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/animation/show')

@app.route('/animation/edit', methods=['GET'])
def edit_animation():
    print('''affichage du formulaire pour modifier une animation''')
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_animation, nom_animation, nb_places_disponibles, date_animation, id_atelier, id_adresse
    FROM animation
    WHERE id_animation=%s;'''
    tuple_param = (id,)
    mycursor.execute(sql, tuple_param)
    animation = mycursor.fetchone()
    sql = ''' SELECT id_atelier, nom_atelier FROM atelier ORDER BY nom_atelier;'''
    mycursor.execute(sql)
    ateliers = mycursor.fetchall()
    sql = ''' SELECT id_adresse, nom_rue, numero_rue FROM adresse ORDER BY nom_rue;'''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()
    return render_template('animation/edit_animation.html', animation=animation, ateliers=ateliers, adresses=adresses)

@app.route('/animation/edit', methods=['POST'])
def valid_edit_animation():
    print('''modification de l'animation''')
    id = request.form.get('id')
    nom_animation = request.form.get('nom_animation')
    nb_places_disponibles = request.form.get('nb_places_disponibles')
    date_animation = request.form.get('date_animation')
    id_atelier = request.form.get('id_atelier')
    id_adresse = request.form.get('id_adresse')
    mycursor = get_db().cursor()
    tuple_param = (nom_animation, nb_places_disponibles, date_animation, id_atelier, id_adresse, id)
    sql = '''UPDATE animation
    SET nom_animation = %s, nb_places_disponibles = %s, date_animation = %s, id_atelier = %s, id_adresse = %s
    WHERE id_animation=%s;'''
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/animation/show')

@app.route('/animation/delete')
def delete_animation():
    print('''suppression d'une animation''')
    id = request.args.get('id', 0)
    mycursor = get_db().cursor()
    tuple_param = (id,)
    sql = "DELETE FROM animer WHERE animation_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM participer WHERE animation_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM animation WHERE id_animation=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/animation/show')


#==============PARTICIPANT===========
@app.route('/participant/show')
def show_participant():
    mycursor = get_db().cursor()
    sql = ''' SELECT participant.id_participant, participant.prenom_participant, participant.nom_participant,
    participant.adresse_mail_participant, participant.telephone, participant.present,
    adresse.nom_rue, adresse.numero_rue
    FROM participant
    JOIN adresse ON participant.id_adresse = adresse.id_adresse
    ORDER BY participant.nom_participant;'''
    mycursor.execute(sql)
    participants = mycursor.fetchall()
    return render_template('participant/show_participant.html', participants=participants)

@app.route('/participant/add', methods=['GET'])
def add_participant():
    print('''affichage du formulaire pour ajouter un participant''')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_adresse, nom_rue, numero_rue FROM adresse ORDER BY nom_rue;'''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()
    return render_template('participant/add_participant.html', adresses=adresses)

@app.route('/participant/add', methods=['POST'])
def valid_add_participant():
    print('''ajout du participant''')
    prenom_participant = request.form.get('prenom_participant')
    nom_participant = request.form.get('nom_participant')
    adresse_mail_participant = request.form.get('adresse_mail_participant')
    telephone = request.form.get('telephone')
    present = request.form.get('present', 0)
    id_adresse = request.form.get('id_adresse')
    mycursor = get_db().cursor()
    tuple_param = (prenom_participant, nom_participant, adresse_mail_participant, telephone, present, id_adresse)
    sql = '''INSERT INTO participant(id_participant, prenom_participant, nom_participant, adresse_mail_participant, telephone, present, id_adresse)
    VALUES (NULL, %s, %s, %s, %s, %s, %s);'''
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/participant/show')

@app.route('/participant/edit', methods=['GET'])
def edit_participant():
    print('''affichage du formulaire pour modifier un participant''')
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_participant, prenom_participant, nom_participant, adresse_mail_participant, telephone, present, id_adresse
    FROM participant
    WHERE id_participant=%s;'''
    tuple_param = (id,)
    mycursor.execute(sql, tuple_param)
    participant = mycursor.fetchone()
    sql = ''' SELECT id_adresse, nom_rue, numero_rue FROM adresse ORDER BY nom_rue;'''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()
    return render_template('participant/edit_participant.html', participant=participant, adresses=adresses)

@app.route('/participant/edit', methods=['POST'])
def valid_edit_participant():
    print('''modification du participant''')
    id = request.form.get('id')
    prenom_participant = request.form.get('prenom_participant')
    nom_participant = request.form.get('nom_participant')
    adresse_mail_participant = request.form.get('adresse_mail_participant')
    telephone = request.form.get('telephone')
    present = request.form.get('present', 0)
    id_adresse = request.form.get('id_adresse')
    mycursor = get_db().cursor()
    tuple_param = (prenom_participant, nom_participant, adresse_mail_participant, telephone, present, id_adresse, id)
    sql = '''UPDATE participant
    SET prenom_participant = %s, nom_participant = %s, adresse_mail_participant = %s, telephone = %s, present = %s, id_adresse = %s
    WHERE id_participant=%s;'''
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/participant/show')

@app.route('/participant/delete')
def delete_participant():
    print('''suppression d'un participant''')
    id = request.args.get('id', 0)
    mycursor = get_db().cursor()
    tuple_param = (id,)
    sql = "DELETE FROM participer WHERE participant_id=%s;"
    mycursor.execute(sql, tuple_param)
    sql = "DELETE FROM participant WHERE id_participant=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/participant/show')


#==========================ANIMER (animateur <-> animation)=====
@app.route('/animer/show')
def show_animer():
    mycursor = get_db().cursor()
    sql = ''' SELECT animer.animateur_id, animer.animation_id,
    animateur.nom_animateur, animateur.prenom_animateur, animation.nom_animation
    FROM animer
    JOIN animateur ON animer.animateur_id = animateur.id_animateur
    JOIN animation ON animer.animation_id = animation.id_animation
    ORDER BY animation.nom_animation;'''
    mycursor.execute(sql)
    animers = mycursor.fetchall()
    return render_template('animer/show_animer.html', animers=animers)

@app.route('/animer/add', methods=['GET'])
def add_animer():
    print('''affichage du formulaire pour associer un animateur à une animation''')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_animateur, nom_animateur, prenom_animateur FROM animateur ORDER BY nom_animateur;'''
    mycursor.execute(sql)
    animateurs = mycursor.fetchall()
    sql = ''' SELECT id_animation, nom_animation FROM animation ORDER BY nom_animation;'''
    mycursor.execute(sql)
    animations = mycursor.fetchall()
    return render_template('animer/add_animer.html', animateurs=animateurs, animations=animations)

@app.route('/animer/add', methods=['POST'])
def valid_add_animer():
    print('''ajout du lien animateur / animation''')
    animateur_id = request.form.get('animateur_id')
    animation_id = request.form.get('animation_id')
    mycursor = get_db().cursor()
    tuple_param = (animateur_id, animation_id)
    sql = "INSERT INTO animer(animateur_id, animation_id) VALUES (%s, %s);"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/animer/show')

@app.route('/animer/delete')
def delete_animer():
    print('''suppression du lien animateur / animation''')
    animateur_id = request.args.get('animateur_id', 0)
    animation_id = request.args.get('animation_id', 0)
    mycursor = get_db().cursor()
    tuple_param = (animateur_id, animation_id)
    sql = "DELETE FROM animer WHERE animateur_id=%s AND animation_id=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/animer/show')


#====S_OCCUPER (animateur <-> atelier)=================
@app.route('/s_occuper/show')
def show_s_occuper():
    mycursor = get_db().cursor()
    sql = ''' SELECT s_occuper.animateur_id, s_occuper.atelier_id,
    animateur.nom_animateur, animateur.prenom_animateur, atelier.nom_atelier
    FROM s_occuper
    JOIN animateur ON s_occuper.animateur_id = animateur.id_animateur
    JOIN atelier ON s_occuper.atelier_id = atelier.id_atelier
    ORDER BY atelier.nom_atelier;'''
    mycursor.execute(sql)
    s_occupers = mycursor.fetchall()
    return render_template('s_occuper/show_s_occuper.html', s_occupers=s_occupers)

@app.route('/s_occuper/add', methods=['GET'])
def add_s_occuper():
    print('''affichage du formulaire pour associer un animateur à un atelier''')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_animateur, nom_animateur, prenom_animateur FROM animateur ORDER BY nom_animateur;'''
    mycursor.execute(sql)
    animateurs = mycursor.fetchall()
    sql = ''' SELECT id_atelier, nom_atelier FROM atelier ORDER BY nom_atelier;'''
    mycursor.execute(sql)
    ateliers = mycursor.fetchall()
    return render_template('s_occuper/add_s_occuper.html', animateurs=animateurs, ateliers=ateliers)

@app.route('/s_occuper/add', methods=['POST'])
def valid_add_s_occuper():
    print('''ajout du lien animateur / atelier''')
    animateur_id = request.form.get('animateur_id')
    atelier_id = request.form.get('atelier_id')
    mycursor = get_db().cursor()
    tuple_param = (animateur_id, atelier_id)
    sql = "INSERT INTO s_occuper(animateur_id, atelier_id) VALUES (%s, %s);"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/s_occuper/show')

@app.route('/s_occuper/delete')
def delete_s_occuper():
    print('''suppression du lien animateur / atelier''')
    animateur_id = request.args.get('animateur_id', 0)
    atelier_id = request.args.get('atelier_id', 0)
    mycursor = get_db().cursor()
    tuple_param = (animateur_id, atelier_id)
    sql = "DELETE FROM s_occuper WHERE animateur_id=%s AND atelier_id=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/s_occuper/show')


#==============FORMER (animateur <-> formateur)=================
@app.route('/former/show')
def show_former():
    mycursor = get_db().cursor()
    sql = ''' SELECT former.animateur_id, former.formateur_id,
    animateur.nom_animateur, animateur.prenom_animateur,
    formateur.nom_formateur, formateur.prenom_formateur
    FROM former
    JOIN animateur ON former.animateur_id = animateur.id_animateur
    JOIN formateur ON former.formateur_id = formateur.id_formateur
    ORDER BY formateur.nom_formateur;'''
    mycursor.execute(sql)
    formers = mycursor.fetchall()
    return render_template('former/show_former.html', formers=formers)

@app.route('/former/add', methods=['GET'])
def add_former():
    print('''affichage du formulaire pour associer un animateur à un formateur''')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_animateur, nom_animateur, prenom_animateur FROM animateur ORDER BY nom_animateur;'''
    mycursor.execute(sql)
    animateurs = mycursor.fetchall()
    sql = ''' SELECT id_formateur, nom_formateur, prenom_formateur FROM formateur ORDER BY nom_formateur;'''
    mycursor.execute(sql)
    formateurs = mycursor.fetchall()
    return render_template('former/add_former.html', animateurs=animateurs, formateurs=formateurs)

@app.route('/former/add', methods=['POST'])
def valid_add_former():
    print('''ajout du lien animateur / formateur''')
    animateur_id = request.form.get('animateur_id')
    formateur_id = request.form.get('formateur_id')
    mycursor = get_db().cursor()
    tuple_param = (animateur_id, formateur_id)
    sql = "INSERT INTO former(animateur_id, formateur_id) VALUES (%s, %s);"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/former/show')

@app.route('/former/delete')
def delete_former():
    print('''suppression du lien animateur / formateur''')
    animateur_id = request.args.get('animateur_id', 0)
    formateur_id = request.args.get('formateur_id', 0)
    mycursor = get_db().cursor()
    tuple_param = (animateur_id, formateur_id)
    sql = "DELETE FROM former WHERE animateur_id=%s AND formateur_id=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/former/show')


#==============TRAVAILLER (animateur <-> profession)
@app.route('/travailler/show')
def show_travailler():
    mycursor = get_db().cursor()
    sql = ''' SELECT travailler.animateur_id, travailler.profession_id,
    animateur.nom_animateur, animateur.prenom_animateur, profession.nom_profession
    FROM travailler
    JOIN animateur ON travailler.animateur_id = animateur.id_animateur
    JOIN profession ON travailler.profession_id = profession.id_profession
    ORDER BY animateur.nom_animateur;'''
    mycursor.execute(sql)
    travaillers = mycursor.fetchall()
    return render_template('travailler/show_travailler.html', travaillers=travaillers)

@app.route('/travailler/add', methods=['GET'])
def add_travailler():
    print('''affichage du formulaire pour associer un animateur à une profession''')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_animateur, nom_animateur, prenom_animateur FROM animateur ORDER BY nom_animateur;'''
    mycursor.execute(sql)
    animateurs = mycursor.fetchall()
    sql = ''' SELECT id_profession, nom_profession FROM profession ORDER BY nom_profession;'''
    mycursor.execute(sql)
    professions = mycursor.fetchall()
    return render_template('travailler/add_travailler.html', animateurs=animateurs, professions=professions)

@app.route('/travailler/add', methods=['POST'])
def valid_add_travailler():
    print('''ajout du lien animateur / profession''')
    animateur_id = request.form.get('animateur_id')
    profession_id = request.form.get('profession_id')
    mycursor = get_db().cursor()
    tuple_param = (animateur_id, profession_id)
    sql = "INSERT INTO travailler(animateur_id, profession_id) VALUES (%s, %s);"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/travailler/show')

@app.route('/travailler/delete')
def delete_travailler():
    print('''suppression du lien animateur / profession''')
    animateur_id = request.args.get('animateur_id', 0)
    profession_id = request.args.get('profession_id', 0)
    mycursor = get_db().cursor()
    tuple_param = (animateur_id, profession_id)
    sql = "DELETE FROM travailler WHERE animateur_id=%s AND profession_id=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/travailler/show')


#==============PARTICIPER (animation <-> participant, avec notes)=====================================================
@app.route('/participer/show')
def show_participer():
    mycursor = get_db().cursor()
    sql = ''' SELECT participer.animation_id, participer.participant_id, participer.nb_present,
    participer.note_animateur, participer.note_atelier,
    animation.nom_animation, participant.nom_participant, participant.prenom_participant
    FROM participer
    JOIN animation ON participer.animation_id = animation.id_animation
    JOIN participant ON participer.participant_id = participant.id_participant
    ORDER BY animation.nom_animation, participant.nom_participant;'''
    mycursor.execute(sql)
    participers = mycursor.fetchall()
    return render_template('participer/show_participer.html', participers=participers)

@app.route('/participer/add', methods=['GET'])
def add_participer():
    print('''affichage du formulaire pour inscrire un participant à une animation''')
    mycursor = get_db().cursor()
    sql = ''' SELECT id_animation, nom_animation FROM animation ORDER BY nom_animation;'''
    mycursor.execute(sql)
    animations = mycursor.fetchall()
    sql = ''' SELECT id_participant, nom_participant, prenom_participant FROM participant ORDER BY nom_participant;'''
    mycursor.execute(sql)
    participants = mycursor.fetchall()
    return render_template('participer/add_participer.html', animations=animations, participants=participants)

@app.route('/participer/add', methods=['POST'])
def valid_add_participer():
    print('''ajout du lien participant / animation''')
    animation_id = request.form.get('animation_id')
    participant_id = request.form.get('participant_id')
    nb_present = request.form.get('nb_present')
    note_animateur = request.form.get('note_animateur')
    note_atelier = request.form.get('note_atelier')
    mycursor = get_db().cursor()
    tuple_param = (animation_id, participant_id, nb_present, note_animateur, note_atelier)
    sql = '''INSERT INTO participer(animation_id, participant_id, nb_present, note_animateur, note_atelier)
    VALUES (%s, %s, %s, %s, %s);'''
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/participer/show')

@app.route('/participer/edit', methods=['GET'])
def edit_participer():
    print('''affichage du formulaire pour modifier une participation''')
    animation_id = request.args.get('animation_id')
    participant_id = request.args.get('participant_id')
    mycursor = get_db().cursor()
    sql = ''' SELECT participer.animation_id, participer.participant_id, participer.nb_present,
    participer.note_animateur, participer.note_atelier,
    animation.nom_animation, participant.nom_participant, participant.prenom_participant
    FROM participer
    JOIN animation ON participer.animation_id = animation.id_animation
    JOIN participant ON participer.participant_id = participant.id_participant
    WHERE participer.animation_id=%s AND participer.participant_id=%s;'''
    tuple_param = (animation_id, participant_id)
    mycursor.execute(sql, tuple_param)
    participer = mycursor.fetchone()
    return render_template('participer/edit_participer.html', participer=participer)

@app.route('/participer/edit', methods=['POST'])
def valid_edit_participer():
    print('''modification de la participation''')
    animation_id = request.form.get('animation_id')
    participant_id = request.form.get('participant_id')
    nb_present = request.form.get('nb_present')
    note_animateur = request.form.get('note_animateur')
    note_atelier = request.form.get('note_atelier')
    mycursor = get_db().cursor()
    tuple_param = (nb_present, note_animateur, note_atelier, animation_id, participant_id)
    sql = '''UPDATE participer
    SET nb_present = %s, note_animateur = %s, note_atelier = %s
    WHERE animation_id=%s AND participant_id=%s;'''
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/participer/show')

@app.route('/participer/delete')
def delete_participer():
    print('''suppression du lien participant / animation''')
    animation_id = request.args.get('animation_id', 0)
    participant_id = request.args.get('participant_id', 0)
    mycursor = get_db().cursor()
    tuple_param = (animation_id, participant_id)
    sql = "DELETE FROM participer WHERE animation_id=%s AND participant_id=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/participer/show')


if __name__ == '__main__':
    app.run(debug=True, port=5000)