from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.db.models.expressions import RawSQL
from django.template.response import TemplateResponse
from django.utils.text import capfirst

from .models import Company, Employee, for_system_time


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    def history_view(self, request, object_id, extra_context=None):
        from django.contrib.admin.views.main import PAGE_VAR

        # First check if the user can see this history.
        model = self.model
        obj = self.get_object(request, unquote(object_id))
        if obj is None:
            return self._get_obj_does_not_exist_redirect(
                request, model._meta, object_id
            )

        if not self.has_view_or_change_permission(request, obj):
            raise PermissionDenied

        # Then get the history for this object.
        action_list = (
            Company.objects.filter(pk=object_id)
            .annotate(row_start=RawSQL("ROW_START", []), row_end=RawSQL("ROW_END", []))
            .order_by("-row_end")
        )

        with for_system_time("all"):
            # must evaluate
            paginator = self.get_paginator(request, list(action_list), 100)
            page_number = request.GET.get(PAGE_VAR, 1)
            page_obj = paginator.get_page(page_number)
            page_range = paginator.get_elided_page_range(page_obj.number)

        context = {
            **self.admin_site.each_context(request),
            "title": "Change history: %s" % obj,
            "subtitle": None,
            "action_list": page_obj,
            "page_range": page_range,
            "page_var": PAGE_VAR,
            "pagination_required": paginator.count > 100,
            "module_name": str(capfirst(self.opts.verbose_name_plural)),
            "object": obj,
            "opts": self.opts,
            "preserved_filters": self.get_preserved_filters(request),
            **(extra_context or {}),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(request, "clean/history.html", context)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    pass
