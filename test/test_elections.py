from app.crud import elections

class Test_Elections_ElectionAgregat:
    def test_ElectionAgregat_1(self):
        result = elections.ElectionAgregat('Municipales 2020', 'bureau')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_2(self):
        result = elections.ElectionAgregat('Municipales 2020', 'commune')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_3(self):
        result = elections.ElectionAgregat('Municipales 2020', 'canton')
        assert result == 'nuance'

    def test_ElectionAgregat_4(self):
        result = elections.ElectionAgregat('Départementales 2015', 'commune')
        assert result == 'nuance, num_dep_binome_candidat'

    def test_ElectionAgregat_5(self):
        result = elections.ElectionAgregat('Départementales 2015', 'canton')
        assert result == 'nuance, num_dep_binome_candidat'

    def test_ElectionAgregat_6(self):
        result = elections.ElectionAgregat('Départementales 2015', 'circonscription')
        assert result == 'nuance'

    def test_ElectionAgregat_7(self):
        result = elections.ElectionAgregat('Législatives 2017', 'canton')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_8(self):
        result = elections.ElectionAgregat('Législatives 2017', 'circonscription')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_9(self):
        result = elections.ElectionAgregat('Législatives 2017', 'departement')
        assert result == 'nuance'

    def test_ElectionAgregat_10(self):
        result = elections.ElectionAgregat('Régionales 2015', 'departement')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_11(self):
        result = elections.ElectionAgregat('Régionales 2015', 'region')
        assert result == 'nuance'

    def test_ElectionAgregat_12(self):
        result = elections.ElectionAgregat('Régionales 2021', 'departement')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_13(self):
        result = elections.ElectionAgregat('Régionales 2021', 'region')
        assert result == 'nuance'

    def test_ElectionAgregat_14(self):
        result = elections.ElectionAgregat('Européennes 2014', 'canton')
        assert result == 'nuance, nom, prenom'

    def test_ElectionAgregat_15(self):
        result = elections.ElectionAgregat('Européennes 2019', 'region')
        assert result == 'nom_liste'

    def test_ElectionAgregat_16(self):
        result = elections.ElectionAgregat('Présidentielles 2017', 'departement')
        assert result == 'nuance, nom, prenom'
