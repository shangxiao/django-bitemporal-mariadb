from django.db.migrations.operations.base import Operation

# adapted from django-pgtrigger


class SystemVersioning(Operation):
    def __init__(self, model_name, add=True):
        self.model_name = model_name
        self.add = add

    def state_forwards(self, app_label, state):
        state.models[(app_label, self.model_name)].options[
            "system_versioned"
        ] = self.add

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        if self.add:
            schema_editor.add_system_versioning(model)
        else:
            schema_editor.remove_system_versioning(model)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        if self.add:
            schema_editor.remove_system_versioning(model)
        else:
            schema_editor.add_system_versioning(model)

    def describe(self):
        verb = "Add" if self.add else "Remove"
        preposition = "to" if self.add else "from"
        return f"{verb} SYSTEM_VERSIONING {preposition} {self.model_name}"


class MigrationAutodetectorMixin:
    def _detect_changes(self, *args, **kwargs):
        self.altered_triggers = {}
        return super()._detect_changes(*args, **kwargs)

    def generate_altered_options(self):
        super().generate_altered_options()
        for app_label, model_name in sorted(
            self.kept_model_keys | self.kept_proxy_keys
        ):
            old_model_name = self.renamed_models.get(
                (app_label, model_name), model_name
            )
            old_model_state = self.from_state.models[app_label, old_model_name]
            new_model_state = self.to_state.models[app_label, model_name]

            if old_model_state.options.get(
                "system_versioned", False
            ) != new_model_state.options.get("system_versioned", False):
                self.add_operation(
                    app_label,
                    SystemVersioning(
                        model_name=model_name,
                        add=new_model_state.options.get("system_versioned", False),
                    ),
                )
