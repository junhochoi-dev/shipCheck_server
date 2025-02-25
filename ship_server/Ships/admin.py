from django.contrib import admin
from .models import NormalShip, WasteShip, NormalImage, WasteImage, OwnerInfo
from django.utils.html import format_html


class NormalImageInline(admin.TabularInline):
    model = NormalImage


class NormalShipAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'port', 'tons', 'types', 'code',
        'is_vpass', 'is_ais', 'is_vhf', 'is_ff', 'is_train',
        'img_cnt', 'register', 'regit_date', 'is_train',
    )
    search_fields = ['id', 'name']
    inlines = [NormalImageInline, ]


class WasteImageInline(admin.TabularInline):
    model = WasteImage


class WastedShipAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'img_cnt', 'info', 'types', 'lat', 'lon', 'is_train',
        'regit_date', 'register'
    )
    search_fields = ['info', 'id']
    inlines = [WasteImageInline, ]


class NormalImgAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'image_tag', 'n_name', 'register', 'regit_date'
    )
    search_fields = ['n_name__id']

    def image_tag(self, obj):
        if obj.img is None:
            return ""
        return format_html('<img src="{}" height="200px;"width="200px;"/>'.format(obj.img.url))
    image_tag.short_description = 'Image'


class WasteImgAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'image_tag', 'w_id', 'register', 'regit_date',
    )
    search_fields = ['w_id__id']

    def image_tag(self, obj):
        if obj.img is None:
            return ""
        return format_html('<img src="{}" height="200px;"width="200px;"/>'.format(obj.img.url))
    image_tag.short_description = 'Image'


class OwnerInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'own_img_tag', 'agreement_paper_tag', 'own_name', 'phone', 'address', 'registry_date', 'privacy_agree', 'ship',
    )
    search_fields = ['own_name', 'ship__id']

    def own_img_tag(self, obj):
        if obj.own_img == "":
            return ""
        return format_html('<img src="{}" height="200px;"width="200px;"/>'.format(obj.own_img.url))

    def agreement_paper_tag(self, obj):
        if obj.agreement_paper == "":
            return ""
        return format_html('<img src="{}" height="200px;"width="200px;"/>'.format(obj.agreement_paper.url))


admin.site.register(NormalShip, NormalShipAdmin)
admin.site.register(WasteShip, WastedShipAdmin)
admin.site.register(NormalImage, NormalImgAdmin)
admin.site.register(WasteImage, WasteImgAdmin)
admin.site.register(OwnerInfo, OwnerInfoAdmin)
