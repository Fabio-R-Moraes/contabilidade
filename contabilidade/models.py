from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify
from stdimage.models import StdImageField
import uuid

def get_file_path(_instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return filename

class Base(models.Model):
    criado = models.DateField('Data de Criação', auto_now_add=True)
    modificado = models.DateField('Data de Atualização', auto_now=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class Cargo(Base):
    cargo = models.CharField('Cargo', max_length=100)

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'

    def __str__(self):
        return self.cargo

class Equipe(Base):
    nome = models.CharField('Nome', max_length=40)
    sobrenome = models.CharField('Sobrenome', max_length=100)
    dataNascimento = models.DateField('Data de Nascimento')
    email = models.EmailField('E-mail', max_length=100)
    cargo = models.ForeignKey('contabilidade.Cargo', verbose_name='Cargo', on_delete=models.CASCADE, default=0)
    foto = StdImageField('Foto', upload_to=get_file_path, variations={'thumb': {'width': 480, 'height':480, 'crop':True}})

    class Meta:
        verbose_name = 'Equipe'
        verbose_name_plural = 'Equipes'

    def __str__(self):
        return f'{self.nome} {self.sobrenome}'

class Conta(Base):
    CREDITO = 'C'
    DEBITO = 'D'
    tipo_CHOICES = [(CREDITO, 'Crédito'),
    (DEBITO, 'Débito'),]

    tipo = models.CharField('Tipo', max_length=1, choices=tipo_CHOICES, default=DEBITO,)
    nomConta = models.CharField('Nome', max_length=100)
    slug = models.SlugField('Slug',max_length=100, blank=True, editable=False)

    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'

    def __str__(self):
        return self.nomConta

def conta_pre_save(signal, instance, sender, **kwargs):
    instance.slug = slugify(instance.nomConta)

signals.pre_save.connect(conta_pre_save, sender=Conta)

class Nota(Base):
    dataNota = models.DateField('Data')
    contaCredito = models.ForeignKey('contabilidade.Conta', related_name='Credito', verbose_name='Conta Crédito', on_delete=models.CASCADE, default=0)
    contaDebito = models.ForeignKey('contabilidade.Conta', related_name='Debito', verbose_name='Conta Débito', on_delete=models.CASCADE, default=0)
    valor = models.DecimalField('Valor', max_digits=9, decimal_places=2)
    imprimir = models.BooleanField('Imprimir?', default=True)

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'

    def __str__(self):
        return self.dataNota

class Razao(Base):
    nomeConta = models.ForeignKey('contabilidade.Conta', verbose_name='Conta', on_delete=models.CASCADE, default=0)
    periodoInicial = models.DateField('Período Inicial')
    periodoFinal = models.DateField('Período Final')
    saldoAnterior = models.DecimalField('Saldo Anterior', max_digits=9, decimal_places=2)
    entradas = models.DecimalField('Entradas', max_digits=9, decimal_places=2)
    saidas = models.DecimalField('Saídas', max_digits=9, decimal_places=2)
    saldoFinal = models.DecimalField('Saldo Final', max_digits=9, decimal_places=2)
    situacao = models.BooleanField('Situação?', default=True)

    class Meta:
        verbose_name = 'Razao'
        verbose_name_plural = 'Razoes'

    def __str__(self):
        return self.nomeConta
