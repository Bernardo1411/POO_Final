from datetime import datetime
from PIL import Image, ImageTk
import PIL.ImageFile
from PIL.ExifTags import TAGS, GPSTAGS
from typing import List, Tuple
import tkinter
import tkintermapview
import tkinter as tk
from tkinter import filedialog
import os

def converte_graus_para_decimais(tup: Tuple[int, int, int], ref: str) -> float:
    '''
    Função utilitária: converte coordenadas de
    graus, minutos e segundos (tupla) para
    decimais (float).
    '''

    if ref.upper() in ('N', 'E'):
        s = 1
    elif ref.upper() in ('S', 'W'):
        s = -1

    return s * (tup[0] + float(tup[1] / 60) + float(tup[2] / 3600))

class Imagem:
    '''
    Representa uma imagem
    (classe principal do programa).
    '''

    def __init__(self, nome):
        '''
        Inicializa um objeto imagem
        a partir do nome do seu arquivo.
        '''

        self._nome = nome.rsplit('/')[-1]  # nome do arquivo da imagem
        self._data = None  # data de captura da imagem
        self._lat = None  # latitude da captura da imagem
        self._lon = None  # longitude da captura da imagem
        self._city = None
        self._country = None
        self._img = self.abre(nome)
        self.img = ImageTk.PhotoImage(self._img.resize(size=(204, 153)))
        self._processa_EXIF()

    def __repr__(self) -> str:
        '''
        Retorna representação de uma imagem
        em forma de str.
        '''
        return self._nome

    def _processa_EXIF(self) -> None:
        '''
        Processa metadados EXIF contidos no arquivo da imagem
        para extrair informações de data e local de captura.

        Atribui valores aos atributos de instância correspondentes
        à latitude, longitude e data de captura.
        '''
        tup_lat = None
        tup_lon = None
        ref_lat = None
        ref_lon = None
        print(self._nome)
        for c, v in self._img._getexif().items():
            if TAGS.get(c) == 'GPSInfo':
                for gps_cod, gps_dado in v.items():
                    if GPSTAGS.get(gps_cod) == 'GPSLatitude':
                        tup_lat = gps_dado
                    if GPSTAGS.get(gps_cod) == 'GPSLongitude':
                        tup_lon = gps_dado
                    if GPSTAGS.get(gps_cod) == 'GPSLatitudeRef':
                        ref_lat = gps_dado
                    if GPSTAGS.get(gps_cod) == 'GPSLongitudeRef':
                        ref_lon = gps_dado

                self._lat = converte_graus_para_decimais(tup_lat, ref_lat)
                self._lon = converte_graus_para_decimais(tup_lon, ref_lon)
                self._city = tkintermapview.convert_coordinates_to_city(self._lat, self._lon)
                self._country = tkintermapview.convert_coordinates_to_country(self._lat, self._lon)

            if TAGS.get(c) == 'DateTime':
                self._data = datetime.strptime(v, '%Y:%m:%d %H:%M:%S')

    @staticmethod
    def abre(nome: str) -> PIL.ImageFile:
        '''
        Abre imagem a partir de
        arquivo com o nome
        fornecido.
        Retorna objeto imagem
        aberto.
        '''
        return Image.open(nome)

    @property
    def nome(self) -> str:
        '''
        Retorna o nome da imagem.
        '''
        return self._nome

    @property
    def largura(self) -> int:
        '''
        Retorna a largura da imagem.
        '''
        return self._img.width

    @property
    def altura(self) -> int:
        '''
        Retorna a altura da imagem.
        '''
        return self._img.height

    @property
    def tamanho(self) -> Tuple[int, int]:
        '''
        Retorna o tamanho da imagem
        (tupla largura x altura).
        '''
        return (self._img.width, self._img.height)

    @property
    def data(self) -> datetime:
        '''
        Retorna a data em que a imagem
        foi capturada (objeto da classe datetime).
        '''
        return self._data

    @property
    def latitude(self) -> float:
        '''
        Retorna a latitude (em decimais)
        em que a imagem foi capturada
        '''
        return self._lat

    @property
    def longitude(self) -> float:
        '''
        Retorna a longitude (em decimais)
        em que a imagem foi capturada
        '''
        return self._lon
    
    @property
    def city(self) -> str:
        '''
        Retorna a cidade
        em que a imagem foi capturada
        '''
        return self._city
    
    @property
    def country(self) -> str:
        '''
        Retorna o país
        em que a imagem foi capturada
        '''
        return self._country

    def imprime_info(self) -> None:
        '''
        Imprime informações sobre
        a imagem.
        '''
        print(f'Nome: {self._nome}')
        print(f'Largura: {self.largura}')
        print(f'Altura: {self.altura}')
        print(f'Data: {self.data}')
        print(f'Latitude: {self.latitude}')
        print(f'Longitude: {self.longitude}')
        print(f'Latitude: {self.city}')
        print(f'Longitude: {self.country}')
        print('---')

    def redimensiona(self, nv_lar: float, nv_alt: float) -> None:
        '''
        Altera as dimensões do objeto imagem para
        que ele possua novo tamanho dado por
        nv_lar x nv_alt.
        '''
        self._img = self._img.resize((int(nv_lar), int(nv_alt)))

class BDImagens:
    '''
    Representa um banco de dados de
    imagens geoespaciais
    (classe de busca do programa).
    '''

    def __init__(self, idx):
        self._idx = idx
        self._imagens = []

    def processa(self) -> None:
        '''
        Abre cada imagem no arquivo de índice
        e adiciona cada imagem à lista.
        '''
        with open(self._idx, 'r') as file:
            for line in file:
                line = line.strip()
                imagem = Imagem(line)
                self._imagens.append(imagem)

    @property
    def tamanho(self) -> int:
        '''
        Retorna a quantidade de imagem
        no banco de dados.
        '''
        return len(self._imagens)

    def todas(self) -> List[Imagem]:
        '''
        Retorna uma lista contendo
        todas as imagens abertas
        no banco de dados.
        '''
        return self._imagens

    def busca_por_nome(self, texto: str) -> List[Imagem]:
        '''
        Retorna uma lista contendo
        todas as imagens do banco de dados
        cujo nome contenha o texto passado
        como parâmetro.
        '''
        resultados = []
        for imagem in self._imagens:
            if texto in imagem._nome:
                resultados.append(imagem)
        return resultados

    def busca_por_data(self, dini: datetime, dfim: datetime) -> List[Imagem]:
        '''
        Retorna uma lista contendo
        todas as imagens do banco de dados
        cuja data de captura encontra-se entre
        dini (data inicial) e dfim (datafinal).
        '''
        resultados = []
        for imagem in self._imagens:
            if dini <= imagem.data <= dfim:
                resultados.append(imagem)
        return resultados
    
    def buscar_por_cidade(self, city) -> List[Imagem]:
        '''
        Retorna uma lista contendo
        todas as imagens do banco de dados
        relacionada a uma cidade.
        '''
        resultados = []
        for imagem in self._imagens:
            if imagem.city == city:
                resultados.append(imagem)
        return resultados

    def buscar_por_pais(self, country) -> List[Imagem]:
        '''
        Retorna uma lista contendo
        todas as imagens do banco de dados
        relacionada a um país.
        '''
        resultados = []
        for imagem in self._imagens:
            if imagem.country == country:
                resultados.append(imagem)
        return resultados

class View:
    def __init__(self, root) -> None:
        self.root = root
        self.root.title('Locais')
        self.root.geometry('1000x400')
        self.root.configure(padx=20, pady=20)

        self.index_file_path = None

        self.BDImagens = BDImagens('dataset1/index')
        self.BDImagens.processa()

        self.mainSearch = tk.Label(root, text="Buscar por Imagens:")
        self.initDateLabel = tk.Label(root, text="Data Inicial:")
        self.finalDateLabel = tk.Label(root, text="Data Final:")
        self.nomeLabel = tk.Label(root, text="Nome:")
        self.cityLabel = tk.Label(root, text="Cidade:")
        self.countryLabel = tk.Label(root, text="País:")

        self.inputNome = tk.Entry(root)
        self.inputInitDate = tk.Entry(root)
        self.inputFinalDate = tk.Entry(root)
        self.inputCity = tk.Entry(root)
        self.inputCountry = tk.Entry(root)

        self.buttonPesquisar = tk.Button(root, text='Pesquisar', command=self.searchImage)
        self.buttonReset = tk.Button(root, text='Redefinir', command=self.resetInputs)
        self.buttonSelectIndexFile = tk.Button(root, text='Selecionar Arquivo de Índice', command=self.selectIndexFile)

        self.mapview = tkintermapview.TkinterMapView(self.root)
        self.mapview.set_position(0, 0)
        self.mapview.set_zoom(0)

        self.marker = []

        self.mainSearch.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        self.initDateLabel.grid(row=1, column=0, sticky=tk.W)
        self.finalDateLabel.grid(row=2, column=0, sticky=tk.W)
        self.nomeLabel.grid(row=3, column=0, sticky=tk.W)
        self.cityLabel.grid(row=4, column=0, sticky=tk.W)
        self.countryLabel.grid(row=5, column=0, sticky=tk.W)

        self.inputInitDate.grid(row=1, column=1)
        self.inputFinalDate.grid(row=2, column=1)
        self.inputNome.grid(row=3, column=1)
        self.inputCity.grid(row=4, column=1)
        self.inputCountry.grid(row=5, column=1)

        self.buttonPesquisar.grid(row=6, column=0, sticky=tk.W, pady=(20, 0))
        self.buttonReset.grid(row=6, column=1, sticky=tk.W, pady=(20, 0))
        self.buttonSelectIndexFile.grid(row=7, column=0, columnspan=2, pady=(20, 0))

        self.mapview.grid(row=0, column=2, rowspan=7, padx=(20, 0),sticky=tk.N)

    def selectIndexFile(self) -> None:
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        self.index_file_path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[('Index Files', 'index')])
        if self.index_file_path:
            self.BDImagens = BDImagens(self.index_file_path)
            self.BDImagens.processa()

    def searchImage(self) -> None:
        mstringNome = self.inputNome.get()
        mstringInitDate = self.inputInitDate.get()
        mstringFinalDate = self.inputFinalDate.get()
        mstringCity = self.inputCity.get()
        mstringCountry = self.inputCountry.get()

        if mstringNome:
            images = self.BDImagens.busca_por_nome(mstringNome)
        elif mstringInitDate and mstringFinalDate:
            d1 = datetime.strptime(mstringInitDate, '%Y-%m-%d')
            d2 = datetime.strptime(mstringFinalDate, '%Y-%m-%d')
            images = self.BDImagens.busca_por_data(d1, d2)
        elif mstringCity:
            images = self.BDImagens.buscar_por_cidade(mstringCity)
        elif mstringCountry:
            images = self.BDImagens.buscar_por_pais(mstringCountry)
        else:
            images = self.BDImagens.todas()

        self.showImagesOnMap(images)

    def showImagesOnMap(self, images: List[Imagem]) -> None:
        self.mapview.set_position(0, 0)
        self.mapview.set_zoom(0)
        self.mapview.delete_all_marker()

        col = 10
        ln = 0
        idx = 0

        for image in images:
            lb_img = tk.Label(self.root, image=image.img)
            lb_img.grid(row=ln, column=col, rowspan=2, padx=(20, 0), sticky=tk.W+tk.N)
            self.mapview.set_marker(image.latitude, image.longitude, text=image.nome)
            self.mapview.set_position(image.latitude, image.longitude)
            self.mapview.set_address(image.nome)
            self.mapview.set_zoom(8)
            if idx%2 != 0:
                col = 10
                ln = ln + 2
            else:
                col = col + 2
            
            idx = idx + 1

    def resetInputs(self) -> None:
        self.inputNome.delete(0, tk.END)
        self.inputInitDate.delete(0, tk.END)
        self.inputFinalDate.delete(0, tk.END)
        self.inputCity.delete(0, tk.END)
        self.inputCountry.delete(0, tk.END)

        self.mapview.set_position(0, 0)
        self.mapview.set_zoom(0)
        self.mapview.delete_all_marker()

def main():
    root = tk.Tk()
    View(root)
    root.mainloop()

if __name__ == '__main__':
    main()
