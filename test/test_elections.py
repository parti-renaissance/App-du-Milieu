from app.crud import elections

class Test_Elections_ElectionAgregat:
    def test_ElectionAgregat_1():
        result = elections.ElectionAgregat('Municipales 2020', 'bureau')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_2():
        result = elections.ElectionAgregat('Municipales 2020', 'commune')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_3():
        result = elections.ElectionAgregat('Municipales 2020', 'canton')
        assert result == 'nuance'

    def test_ElectionAgregat_4():
        result = elections.ElectionAgregat('Départementales 2015', 'commune')
        assert result == 'nuance, num_dep_binome_candidat'

    def test_ElectionAgregat_5():
        result = elections.ElectionAgregat('Départementales 2015', 'canton')
        assert result == 'nuance, num_dep_binome_candidat'

    def test_ElectionAgregat_6():
        result = elections.ElectionAgregat('Départementales 2015', 'circonscription')
        assert result == 'nuance'

    def test_ElectionAgregat_7():
        result = elections.ElectionAgregat('Législatives 2017', 'canton')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_8():
        result = elections.ElectionAgregat('Législatives 2017', 'circonscription')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_9():
        result = elections.ElectionAgregat('Législatives 2017', 'departement')
        assert result == 'nuance'

    def test_ElectionAgregat_10():
        result = elections.ElectionAgregat('Régionales 2015', 'departement')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_11():
        result = elections.ElectionAgregat('Régionales 2015', 'region')
        assert result == 'nuance'

    def test_ElectionAgregat_12():
        result = elections.ElectionAgregat('Régionales 2021', 'departement')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_13():
        result = elections.ElectionAgregat('Régionales 2021', 'region')
        assert result == 'nuance'

    def test_ElectionAgregat_14():
        result = elections.ElectionAgregat('Européennes 2014', 'canton')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_15():
        result = elections.ElectionAgregat('Européennes 2019', 'region')
        assert result == 'nom_liste'

    def test_ElectionAgregat_16():
        result = elections.ElectionAgregat('Présidentielles 2017', 'departement')
        assert result == 'nuance, nom, prenom'
