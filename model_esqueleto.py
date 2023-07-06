from datetime import datetime
from PIL import Image
import PIL.ImageFile
from PIL.ExifTags import TAGS, GPSTAGS
from typing import List, Tuple

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
        self._img = self.abre(nome)
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

def main():
    bd = BDImagens('dataset1/index')
    bd.processa()

    # Mostra as informações de todas as imagens do banco de dados
    print('Imagens do Banco de Dados:')
    for img in bd.todas():
        img.imprime_info()

    # Mostra os nomes das imagens que possuam texto no seu nome
    texto = '06'
    print(f'Imagens com o texto "{texto}" no nome:')
    for img in bd.busca_por_nome(texto):
        print(img.nome)

    # Mostra as datas das imagens capturadas entre d1 e d2
    d1 = datetime(2021, 1, 1)
    d2 = datetime(2023, 1, 1)
    print(f'Imagens capturadas entre {d1} e {d2}:')
    for img in bd.busca_por_data(d1, d2):
        print(img.data)

if __name__ == '__main__':
    main()
