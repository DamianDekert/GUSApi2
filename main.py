from litex.regon import REGONAPI
import customtkinter
from tkinter import *
from tkinter import messagebox
from PIL import Image
import sys, os

def validate_nip(nip_str):
  '''Checking NIP number correction'''
  nip_str = nip_str.replace('-', '')
  if len(nip_str) != 10 or not nip_str.isdigit(): 
    return False
  digits = [int(i) for i in nip_str]
  weights = (6, 5, 7, 2, 3, 4, 5, 6, 7)
  check_sum = sum(d * w for d, w in zip(digits, weights)) % 11
  return check_sum == digits[9]

def getData(userNip, path="", event=None) :

    for output in outputs.values():
        output.delete("1.0", END)

    api = REGONAPI('https://wyszukiwarkaregontest.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc')

    api.login('abcde12345abcde12345')

    try:
        entities = api.search(nip=userNip)
    except:
        if validate_nip(userNip):
            messagebox.showerror("Nieznaleziono w bazie", "Nie znaleziono danych w bazie")
        else:
            if len(userNip) != 10:
                messagebox.showerror('Niepoprawny NIP', 'Numer NIP ma długość 10 znaków.')
            else:
                messagebox.showerror('Niepoprawny NIP', "Wprowadzony numer NIP jest nieprawidłowy." +
                "\n(Nie spełnia warunku cyfry kontrolnej."+
                " Prawdopodobna przyczyna: błąd typu literówka.)")
    else:

        if len(sys.argv) > 1 and sys.argv[2]=="--S":
            outputs['nazwa'] = entities[0].Nazwa
            try:
                if entities[0].NrLokalu == '':
                    outputs['adres'] = entities[0].Ulica + ' ' + str(entities[0].NrNieruchomosci)
                else:
                    outputs['adres'] = entities[0].Ulica + ' ' + str(entities[0].NrNieruchomosci) + ' / ' + str(entities[0].NrLokalu)
            except AttributeError:
                if entities[0].NrNieruchomosci != '' and entities[0].NrLokalu != '':
                    outputs['adres'] = entities[0].Ulica + ' ' + str(entities[0].NrNieruchomosci) + ' / ' + str(entities[0].NrLokalu)
                elif entities[0].NrNieruchomosci != '':
                    outputs['miasto'] = entities[0].Miejscowosc + " " + str(entities[0].NrNieruchomosci)
                else:
                    outputs['adres'] =  ""
            else: 
                outputs['miasto'] = entities[0].Miejscowosc
            finally:

                outputs['kodPocztowy'] = entities[0].KodPocztowy
    
                outputs['wojewodztwo'] = entities[0].Wojewodztwo
    
                outputs['regon'] = entities[0].Regon
    
        else:
            
            outputs['nazwa'].insert(INSERT, entities[0].Nazwa)

            try:
                if entities[0].NrLokalu == '':
                    outputs['adres'].insert(INSERT, entities[0].Ulica + ' ' + str(entities[0].NrNieruchomosci))    
                else:
                    outputs['adres'].insert(INSERT, entities[0].Ulica + ' ' + str(entities[0].NrNieruchomosci) + ' / ' + str(entities[0].NrLokalu))
            except AttributeError:
                if entities[0].NrNieruchomosci != '' and entities[0].NrLokalu != '':
                    outputs['adres'].insert(INSERT, entities[0].Ulica + ' ' + str(entities[0].NrNieruchomosci) + ' / ' + str(entities[0].NrLokalu))
                elif entities[0].NrNieruchomosci != '':
                    outputs['miasto'].insert(INSERT, entities[0].Miejscowosc + " " + str(entities[0].NrNieruchomosci))
                else:
                    outputs['adres'].insert(INSERT, "")
            else: 
                outputs['miasto'].insert(INSERT, entities[0].Miejscowosc)
            finally:

                outputs['kodPocztowy'].insert(INSERT, entities[0].KodPocztowy)
    
                outputs['wojewodztwo'].insert(INSERT, entities[0].Wojewodztwo)
    
                outputs['regon'].insert(INSERT, entities[0].Regon)
    
    with open(path + userNip + ".ini", "w") as f:
        f.write("[DANE]\n")
        if len(sys.argv) > 1 and sys.argv[2]=="--S":
            for k, v in outputs.items():
                f.writelines(k + "=" + str(v) + "\n")
        else:
            for k, v in outputs.items():
                f.write(str(k) + "=" + str(v.get("1.0",END)))
                
def do_popup(event, m):
    '''Burger menu'''
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()

def copy_text(root):
    try:
        selected = root.selection_get()
        root.clipboard_clear()
        root.clipboard_append(selected)
    except:
        root.clipboard_clear()
            
def guiApp(outputs):
    '''GUI version with Tkinter'''
    outputFont = 13 
    outpuPadding = 8
    outputTextWeight = 600

    customtkinter.set_appearance_mode('system')
    customtkinter.set_default_color_theme('dark-blue')


    root = customtkinter.CTk()
    root.title ("Nip APP")
    root.geometry('800x500')
    root.resizable(False,False)

    logo = resource_path("logo.png")
    img = PhotoImage("logo.png")

    frame = customtkinter.CTkFrame(root)
    frame.pack(fill=BOTH, expand=True)

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.columnconfigure(2, weight=1)
    frame.columnconfigure(3, weight=1)


    # img = customtkinter.CTkImage(Image.open(r"./logo.png"), size=(80, 80))
    img = customtkinter.CTkImage(Image.open(logo), size=(80, 80))

    logolabel = customtkinter.CTkLabel(master=frame, image=img, text="")
    logolabel.grid(column=0, row=0, sticky=W, padx=10, pady=10)

    m = Menu(root, tearoff=False)
    m.add_command(label="Kopiuj", command = lambda: copy_text(root))
    root.bind("<Button-3>", lambda event:do_popup(event, m))

    Mainlabel = customtkinter.CTkLabel(master=frame, text='Wyszukiwarka danych', font=("Roboto", 24))
    Mainlabel.grid(columnspan=4, row=0, ipady = 5)

    L1 = customtkinter.CTkLabel(master=frame, text="NIP:", font=("Roboto", 18))
    L1.grid(column=0, row=1, sticky=E, ipadx = 15)

    userNipEntry = customtkinter.CTkEntry(master=frame, placeholder_text="Wpisz NIP")
    userNipEntry.grid(column=1, row=1, sticky=W, pady=15)
    button = customtkinter.CTkButton(master=frame, text='Pobierz dane z GUS', command=lambda: getData(userNipEntry.get(),""))
    root.bind('<Return>', lambda event: getData(userNipEntry.get(),"", event))
    button.grid(column=2, row=1, sticky=W)

    # LAYOUT----------------------------------------------------------------------------------------------------------------
    # NAZWA------------------------------------------

    nameLabel = customtkinter.CTkLabel(master=frame, text="NAZWA: ", font=("Roboto", outputFont, 'bold')) 
    nameLabel.grid(column = 0, row = 2, pady = outpuPadding) 

    outputs['nazwa'] = customtkinter.CTkTextbox(master=frame, font=("Roboto", outputFont), width=outputTextWeight, height=1)
    outputs['nazwa'].grid(columnspan = 4, row = 2, pady = outpuPadding, sticky=E, padx=20) 

    # ADRES-------------------------------------------

    addressLabel = customtkinter.CTkLabel(master=frame, text="ADRES: ", font=("Roboto", outputFont, 'bold'))
    addressLabel.grid(column = 0, row = 3, pady = outpuPadding) 

    outputs['adres'] = customtkinter.CTkTextbox(master=frame, font=("Roboto", outputFont), width=outputTextWeight, height=1)
    outputs['adres'].grid(columnspan = 4, row = 3, pady=outpuPadding, sticky=E, padx=20)

    # KOD POCZTOWY -----------------------------------

    postCodeLabel = customtkinter.CTkLabel(master=frame, text="KOD POCZTOWY:", font=("Roboto", outputFont, 'bold'))
    postCodeLabel.grid(column = 0, row = 4, pady = outpuPadding, padx=55, sticky=W) 

    outputs['kodPocztowy'] = customtkinter.CTkTextbox(master=frame, font=("Roboto", outputFont), width=outputTextWeight, height=1)
    outputs['kodPocztowy'].grid(columnspan = 4, row = 4, pady=outpuPadding, sticky=E, padx=20) 

    # MIASTO ------------------------------------------

    cityLabel = customtkinter.CTkLabel(master=frame, text="MIASTO:  ", font=("Roboto", outputFont, 'bold'))
    cityLabel.grid(column = 0, row = 5, pady = outpuPadding) 

    outputs['miasto'] = customtkinter.CTkTextbox(master=frame, font=("Roboto", outputFont), width=outputTextWeight, height=1)
    outputs['miasto'].grid(columnspan = 4, row = 5, pady=outpuPadding, sticky=E, padx=20)

    # WOJEWÓDZTWO ---------------------------------------------

    provinceLabel = customtkinter.CTkLabel(master=frame, text="WOJEWÓDZTWO:", font=("Roboto", outputFont, 'bold'))
    provinceLabel.grid(column = 0, row = 6, pady = outpuPadding, padx=55, sticky=W) 

    outputs['wojewodztwo'] = customtkinter.CTkTextbox(master=frame, font=("Roboto", outputFont), width=outputTextWeight, height=1)
    outputs['wojewodztwo'].grid(columnspan = 4, row = 6, pady=outpuPadding, sticky=E, padx=20) 

    # REGON ---------------------------------------------

    regonLabel = customtkinter.CTkLabel(master=frame, text="REGON:  ", font=("Roboto", outputFont, 'bold'))
    regonLabel.grid(column = 0, row = 7, pady = outpuPadding)

    outputs['regon'] = customtkinter.CTkTextbox(master=frame, font=("Roboto", outputFont), width=outputTextWeight, height=1)
    outputs['regon'].grid(columnspan = 4, row = 7, pady=outpuPadding, sticky=E, padx=20) 

    # PODANIE ARGUMENTU W KONSOLI -----------------------

    if len(sys.argv) > 1 and sys.argv[2]=="--R": 
        userNipEntry.insert(INSERT, sys.argv[1])
        userNipEntry.configure(state=DISABLED)
        button.invoke()
        button.grid_forget()
        nameLabel.grid(padx=120, sticky=W)
        addressLabel.grid(padx=120, sticky=W)
        regonLabel.grid(padx=120, sticky=W)
        cityLabel.grid(padx=110, sticky=W)
        root.unbind('<Return>')


    root.mainloop()

def resource_path(relative_path):
    '''Set a PATH to png to resolve problem with png direction'''
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

'''Two version of app first with GUI second which only save data in output file without GUI'''
'''--------------------------------------------------------------------------------------------------------------'''
'''TO DO'''
'''Get data do poprawy zapis do pliku powininen być w innej funkcji'''
'''Guid app do poprawy warunek parametrów jeżeli --R powinien być sprawdzany w main'''
'''--S   --->     Parametr  Save działanie programu ma polegać na zapisie danych do zewnętrznego pliku bez GUI'''
'''--R   --->     Parametr Read działanie programu ma polegać na uruchumieniu GUI z wypełnionym już numerem NIP oraz danymi w programie'''
'''W przypadku --R edycja parametru NIPu oraz przycisk mają nie być widoczne dla użytkonika'''
'''4 parametrem w wywołaniu programu jest w domyśle ściężka do pliku wraz z nazwą użytkownika, po której NIP dodawny jest automatycznie'''
'''Wyjściowy format pliku to .ini'''


outputs={}
consoleValues = len(sys.argv)

if consoleValues == 3:
    
    if sys.argv[2] == "--S":
        getData(sys.argv[1])
    elif sys.argv[2] == "--R":
        guiApp(outputs)

if consoleValues == 4 and sys.argv[2]=="--S":
        path = sys.argv[3]
        getData(sys.argv[1], path)

if consoleValues < 3: 
    guiApp(outputs)
