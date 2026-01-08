from django.contrib import admin
from .models import Egresado, Documento, EgresadoDocumento, Etapa, Plan, GrupoPlan, OpcionTitulacion

class EgresadoDocumentoInline(admin.TabularInline):
    model = EgresadoDocumento
    extra = 0

@admin.register(Egresado)
class EgresadoAdmin(admin.ModelAdmin):
    # Muestra todos los campos excepto 'etapa', y en su lugar muestra 'etapa_nombre'
    fields = (
        'usuario',
        'curp',
        'numero_control',
        'nombre',
        'primer_apellido',
        'segundo_apellido',
        'genero',
        'etapa',
        'ano_de_egreso',
        'periodo_escolar_de_egreso',
        'grupo_plan',
        'opcion_titulacion',
    )
    list_display = ('nombre', 'primer_apellido', 'curp',)
    search_fields = ('numero_control', 'nombre', 'primer_apellido', 'curp',)
    inlines = [EgresadoDocumentoInline]

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descripcion')
    search_fields = ('titulo',)


@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'orden')
    search_fields = ('nombre',)
    ordering = ('orden',)


class PlanInline(admin.TabularInline):
    model = Plan
    extra = 0

@admin.register(GrupoPlan)
class GrupoPlanAdmin(admin.ModelAdmin):
    fields = ('nombre', 'descripcion')
    list_display = ('nombre',)
    search_fields = ('nombre',)
    inlines = [PlanInline]

@admin.register(OpcionTitulacion)
class OpcionTitulacionAdmin(admin.ModelAdmin):
    fields = ('nombre', 'descripcion')
    list_display = ('nombre',)
    search_fields = ('nombre',)