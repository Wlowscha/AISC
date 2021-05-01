
import pandas as pd
from mendeleev import element

def SuperCon(sc_path = '../data/raw/supercon_tot.csv'):
    """
    carica un dataset con gli atomi che compongono i materiali superconduttori e la loro temperatura critica

    output:
          dataset
    """

    sc_dataframe = pd.read_csv(sc_path)
    return sc_dataframe


def PeriodicTable(max_index_atom=109,max_missing_value=30):
    """
    carica i dataset dei composti superconduttori e la tavola periodica
    features atomiche disponibili:'atomic_number', 'atomic_volume', 'block', 'density',
       'dipole_polarizability', 'electron_affinity', 'evaporation_heat',
       'fusion_heat', 'group_id', 'lattice_constant', 'lattice_structure',
       'melting_point', 'period', 'specific_heat', 'thermal_conductivity',
       'vdw_radius', 'covalent_radius_pyykko', 'en_pauling', 'atomic_weight',
       'atomic_radius_rahm', 'valence', 'ionenergies'
    input:
          numero massimo di atomi da caricare (opzionale)
          numero massimo di dati mancanti per feature (opzionale)
    output:
          dataset
    """
    from mendeleev import get_table


    periodic_table = get_table('elements')
    #max_index_atom = 109
    #max_missing_value = 30
    #PROVA: TOLGO "en_pauling","group_id","evaporation_heat"
    prop_atomic_unn = ['annotation','description','name','jmol_color','symbol','is_radioactive','vdw_radius_mm3',
                           'cpk_color','uses','sources','name_origin','discovery_location','covalent_radius_cordero',
                           'discoverers','cas','goldschmidt_class','molcas_gv_color','discovery_year','atomic_radius','series_id',
                           'electronic_configuration','glawe_number','en_ghosh','heat_of_formation','covalent_radius_pyykko_double',
                           'vdw_radius_alvarez','abundance_crust', 'abundance_sea', 'c6_gb','vdw_radius_uff',
                           'dipole_polarizability_unc','boiling_point','pettifor_number','mendeleev_number']

    ionenergies_col= []
#non è disponibile il dato per i maggiore di 109
    for i in range(1,max_index_atom):
        el = element(i)
        el = el.ionenergies[1]
        ionenergies_col.append(el)

    valence_col = []
    for i in range(1,max_index_atom):
        el = element(i)
        el = el.nvalence()
        valence_col.append(el)

    periodic_table.drop(prop_atomic_unn,axis = 1,inplace=True)
    periodic_table = periodic_table[:(max_index_atom-1)]

    periodic_table['valence'] = valence_col
    periodic_table['ionenergies'] = ionenergies_col


    periodic_table.shape
    col_vuote = []
    mancanti = periodic_table.isna().sum()
    for i in range(mancanti.size):
        if mancanti[i] >= max_missing_value:
            col_vuote.append(mancanti.index[i])


    col_vuote.remove('thermal_conductivity')
    col_vuote.remove('fusion_heat')
    col_vuote.remove('electron_affinity')
    periodic_table.drop(col_vuote,axis = 1,inplace=True)
    periodic_table = periodic_table[:96]

    import numpy as np

    path = "/home/claudio/aisc/project_aisc/data/raw/"
    periodic_table = pd.DataFrame(periodic_table)
    thermal_conductivity = pd.read_csv(path+"thermal_conductivity.csv",header=None)

    thermal_conductivity.replace('QuantityMagnitude[Missing["NotAvailable"]]',np.nan,inplace=True)
    thermal_conductivity.replace('QuantityMagnitude[Missing["Unknown"]]',np.nan,inplace=True)

    specific_heat = pd.read_csv(path+"specific_heat.csv",header = None)

    specific_heat.replace('QuantityMagnitude[Missing["NotAvailable"]]',np.nan,inplace=True)
    specific_heat.replace('QuantityMagnitude[Missing["Unknown"]]',np.nan,inplace=True)

    electron_affinity = pd.read_csv(path+"electron_affinity.csv",header=None)

    electron_affinity.replace('QuantityMagnitude[Missing["NotAvailable"]]',np.nan,inplace=True)
    electron_affinity.replace('QuantityMagnitude[Missing["Unknown"]]',np.nan,inplace=True)

    density = pd.read_csv(path+"density.csv",header=None)

    density.replace('QuantityMagnitude[Missing["NotAvailable"]]',np.nan,inplace=True)
    density.replace('QuantityMagnitude[Missing["Unknown"]]',np.nan,inplace=True)

    for i in range(96):

        if periodic_table["thermal_conductivity"].isna()[i]:
           periodic_table["thermal_conductivity"][i] =thermal_conductivity.values[i]

        if periodic_table["specific_heat"].isna()[i]:
            periodic_table["specific_heat"][i] = specific_heat.astype('float32').values[i]/1000

        if periodic_table["electron_affinity"].isna()[i]:
            periodic_table["electron_affinity"][i] = electron_affinity.astype('float32').values[i]/100

        if periodic_table["density"].isna()[i]:
            periodic_table["density"][i] = density.astype('float32').values[i]/1000


    return periodic_table



def CreateSuperCon(material=False,name='supercon_tot.csv'):
    """Create a dataset of superconductor and non-superconducting materials

    Args:
        material (bool): a flag used to indicate if keep or not the material column
        name (str): the name of the saved file (default is supercon_tot.csv)
    """
    #read data in a column separed format
    supercon = pd.read_csv('../../data/raw/SuperCon_database.dat',delimiter = r"\s+",names = ['formula','tc'])
    #remove rows with nan value on tc
    supercon = supercon.dropna()
    #get duplicated row aggregating them with mean value on critical temperature
    duplicated_row = supercon[supercon.duplicated(subset = ['formula'],keep = False)].groupby(supercon['formula']).aggregate({'tc':'mean'}).reset_index()
    #drop all the duplicated row
    supercon.drop_duplicates(subset = ['formula'],inplace = True,keep = False)
    #compose the entire dataset
    supercon= supercon.append(duplicated_row,ignore_index=True)
    #initialize a dictionary with element symbol,critical_temp,material as keys
    sc_dict={}
    num_element = 96
    for i in range(1,num_element+1):
        sc_dict[element(i).symbol] = []

    sc_dict['material'] = []
    sc_dict['critical_temp'] = []
    #list with all the element symbol
    list_element = list(sc_dict.keys())[:num_element]
    #search element that are put more than one time in a formula
    repeted_values = []
    for i in range(supercon['formula'].shape[0]):

        sc_string = supercon['formula'][i]
        tupl_atom = []
        from_string_to_dict(sc_string,tupl_atom)
        list_atom = []
        for j in range(len(tupl_atom)):
            list_atom.append(tupl_atom[j][0])

        if len(list(set(list_atom))) != len(list_atom):

            repeted_values.append(i)
    #drop repeted element and reset index
    supercon.drop(repeted_values,inplace=True)
    supercon.reset_index(inplace=True)
    #list with the elements symbol
    element_list = list(sc_dict.keys())
    element_list = element_list[:-2]
    element_list = set(element_list)
    #create a dictionary with the quantity of each element on the molecules and relative chemical formula and critical temperature
    for i in range(supercon['formula'].shape[0]):

        sc_string = supercon['formula'][i]
        sc_dict['material'].append(sc_string)
        sc_dict['critical_temp'].append(float(supercon['tc'][i]))
        tupl_atom = []
        from_string_to_dict(sc_string,tupl_atom)
        list_atom = []
        for j in range(len(tupl_atom)):
            list_atom.append(tupl_atom[j][0])

            if tupl_atom[j][0] in list_element:
                sc_dict[tupl_atom[j][0]].append(float(tupl_atom[j][1]))

        element_not_present = element_list - (set(list_atom))

        for el in element_not_present:
            sc_dict[el].append(0)

    sc_dataframe = pd.DataFrame(sc_dict)
    if not material:
        sc_dataframe.drop(axis=1,inplace=True,columns=['material'])
    sc_dataframe.to_csv('../../data/raw/'+name)





def from_string_to_dict(string,lista):
    """add to a list tuples containing elements and the relative quantity presence

    Args:
        string (str): string of the material
        lista (list): list where the couples element, quantity are added
    """
    nums = ['0','1','2','3','4','5','6','7','8','9','.']
    i = 0
    element_name = ''
    element_quantity = ''
    on = True

    while(i<len(string) and on ):
        if string[i] not in nums:

            element_name = element_name + string[i]

            if i == len(string)-1:
                lista.append((element_name,'1'))
                return
            if i+1 < len(string):
                if string[i+1].isupper() :
                    lista.append((element_name,'1'))
                    string = string[i+1:]
                    from_string_to_dict(string,lista)
                    return

            if i == len(string)-1:
                lista.append((element_name,'1'))
                return

        if string[i] in nums:
            element_quantity = ''
            for j in range(len(string)-i):

                if string[i+j] in nums:

                    element_quantity = element_quantity + string[i+j]

                else:
                    on = False


                    break
                if i+j+len(element_name)-1 == len(string):
                    lista.append((element_name,element_quantity))
                    return

        i +=1
    lista.append((element_name,element_quantity))

    if i+j < len(string) and string[i+j-1] != nums :
        string = string[i+j-1:]
        from_string_to_dict(string,lista)
