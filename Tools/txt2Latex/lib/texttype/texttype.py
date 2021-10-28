from typing import List, Tuple, Set
"""Erlaubt das einfache Arbeiten mit texen zugeordneten daten.
Geschrieben, um Text zeilenweise zu klassifizieren"""

class texttype():
    def __init__(self, data: List[Tuple[str]], gew_typ=None):
        """Data: [('string', typ1, Typ2, ...), ...]
        gew_typ: None oder liste von typen. 
        Der gewählte typ für ein Element wird jeweils ein typ (nicht notwendig aus den typen in data)"""
        self.data = data
        # gewählter typ. Standartmäßig ist kein typ gewählt.
        if gew_typ is None:
            self.gew_typ = [None]*len(self.data)
        else: 
            self.gew_typ = gew_typ
        self.str = []
        self.typ = []
        # Die Arbeitsdatengenerierung frisst Speicher und rechenzeit. Sie wird nur gemacht, wenn nötig
        self.workingDataOK = False    

    def _updateWD(self):
        """bringt die arbeitsdaten ggf. auf den neusten stand"""
        if not self.workingDataOK:
            self._generateWorkingData()#

    def invalidateWD(self):
        """die Arbeitscdaten als veraltet markieren.
        Sie werden bei bedarf neu generiert. 
        Das ist im allgemeinen nur nach manuellen Änderungen nötig"""
        self.workingDataOK = False
        # Speicher sparen:
        self.str = []
        self.typ = []

    def _generateWorkingData(self):
        # Arbeitsdaten generieren. Diese funktion muss in __init__ und ggf. nach Modifikationen aufgerufen werden.
        self.str = []
        self.typ = []
        # Maximale Anzahl der typen, die für einen string gespeichert sind
        self.anz_typen = max(len(frame)-1 for frame in self.data)
        for frame in self.data:
            self.str.append(frame[0])
            self.typ.append(list(frame[1:]) + [None] * (self.anz_typen - len(frame[1:])))
        self.workingDataOK = True

    def __add__(self, other):
        """addition von zwei texttype objekten"""
        return self.__class__(self.data + other.data, gew_typ=self.gew_typ + other.gew_typ)
    
    def __mul__(self, other):
        """Ganzzahlige multiplikation. Hängt das element mehrfach hintereinander"""
        return self.__class__(self.data * other, gew_typ=self.gew_typ * other)

    def _split(self, divider, search_in):
        # helferfunktion für split
        last_index = 0
        erg = []
        all_found = False
        while not all_found:
            try:
                new_index = search_in.index(divider, last_index)
            except ValueError: # Element nicht gefunden, suche wird beendet.
                new_index = -1
                all_found = True
            
            if new_index >= last_index + 1:
                # Zwischen den dividern befindet sich text (standart)
                erg.append(self.__class__(self.data[last_index: new_index], gew_typ=self.gew_typ[last_index: new_index]))
            elif new_index == -1: # letzten Teil gefunden
                if last_index - len(search_in) < -2: # zwischen den letzten beiden dividern befindet sich text
                    erg.append(self.__class__(
                        self.data[last_index: new_index], gew_typ=self.gew_typ[last_index: new_index]))
            last_index = new_index + 1 #erhöhe um eins. Dadurch wird das divider-Element nicht übernommen.
        return erg

    def split(self, divider:str, split_by='gew')->list:
        """# Teilt das Objekt in beliebig viele texttype objekte, ähnlich der split-methode für str.
        Geteilt wird an Elementen vom typ divider. Dieses Elemente sind im Ergebnis nicht enthalten.
        split_by: gew: gewählter typ
                  0:   erste Möglichkeit
                  1:   zweite Möglichkeit
                  …:   und so weiter"""

        # Wir bruchen brauchbare Arbeitsdaten
        self._updateWD()

        if split_by == 'gew':
            return self._split(divider, self.gew_typ)
        elif type(split_by) == int and split_by < self.anz_typen:
            return self._split(divider, list(list(zip(*self.typ))[split_by]))
        else:
            raise AttributeError("split_by="+str(split_by)+" ist icht möglich. Mögliche Argumente für \"Split_By\": \"gew\", " + (n+', ') for n in range(self.anz_typen))
    
    def __getitem__(self, slice):
        return self.__class__(self.data[slice], gew_typ=self.gew_typ[slice])

    def __str__(self):
        erg = ''
        for i in range(len(self.data)):
            erg += self.data[i][0]+'\n'
        return erg
    
    def __len__(self):
        """Anzahl der verwalteten Elemente"""
        return len(self.data)
    
    def choose(self, i:int, typ:str)->None:
        """setze den gewählten typ für das i-te Element"""
        self.gew_typ[i] = typ
    
    def choices(self, i:int)-> List[str]:
        """gibt die sortierte liste aller für das i-te Element vorgeschlagenen typen zurück"""
        self._updateWD()
        return self.typ[i]
    
    def types(self)->Set[str]:
        """Die Menge aller vorkommenden typen"""
        return set(self.gew_typ)
    
    def __iter__(self):
        self.iterator = [self.str.__iter__(), self.gew_typ.__iter__(), self.typ.__iter__()]
    
    def __next__(self):
        return (self.iterator[i].next() for i in range(3))
    
    __doc__ =  """Erlaubt, texten zeilenweise typen zuzuweisen."""

