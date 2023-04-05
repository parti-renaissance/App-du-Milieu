from app.crud import elections

election_aggregat_tests = [
    ('Municipales 2020', 'bureau', 'nuance, nom, prenom'),
    ('Municipales 2020', 'commune', 'nuance, nom, prenom'),
    ('Municipales 2020', 'canton', 'nuance'),
    ('Départementales 2015', 'commune', 'nuance, num_dep_binome_candidat'),
    ('Départementales 2015', 'canton', 'nuance, num_dep_binome_candidat'),
    ('Départementales 2015', 'circonscription', 'nuance'),
    ('Législatives 2017', 'canton', 'nuance, nom, prenom'),
    ('Législatives 2017', 'circonscription', 'nuance, nom, prenom'),
    ('Législatives 2017', 'departement', 'nuance'),
    ('Régionales 2015', 'departement', 'nuance, nom, prenom'),
    ('Régionales 2015', 'region', 'nuance'),
    ('Régionales 2021', 'departement', 'nuance, nom, prenom'),
    ('Régionales 2021', 'region', 'nuance'),
    ('Européennes 2014', 'canton', 'nuance, nom, prenom'),
    ('Européennes 2019', 'region', 'nom_liste'),
    ('Présidentielles 2017', 'departement', 'nuance, nom, prenom')
]

def test_ElectionAgregat():
    for election, agregat, expected_result in election_aggregat_tests:
        result = elections.ElectionAgregat(election, agregat)
        assert result == expected_result
