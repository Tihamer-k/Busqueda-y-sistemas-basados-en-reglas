from tkinter import ttk


class AutocompleteCombobox(ttk.Combobox):

    def __init__(self, *args, **kwargs):
        """
        Inicializa el combobox autocompletado.

        Parámetros:
            - *args: Argumentos posicionales.
            - **kwargs: Argumentos de palabra clave.
        """
        super().__init__(*args, **kwargs)
        self.handle_focusout = None
        self.handle_focusin = None
        self._completion_list = []
        self._original_values = []
        self.bind('<FocusIn>', self.handle_focusin)
        self.bind('<FocusOut>', self.handle_focusout)

    def set_completion_list(self, completion_list):
        """
        Establece la lista de elementos para autocompletar.

        Parámetros:
            - completion_list (list): Lista de elementos para autocompletar.
        """
        self._completion_list = sorted(completion_list, key=str.lower)
        self['values'] = self._completion_list
        self.bind('<KeyRelease>', self.handle_keyrelease)

    def handle_keyrelease(self, event):
        """
        Maneja el evento de liberación de tecla para actualizar la lista de autocompletar.

        Parámetros:
            - event (tkinter.Event): Evento de liberación de tecla.
        """
        if event.keysym in ("Left", "Right", "Up", "Down", "Return"):
            return
        value = self.get().strip().lower()
        if value == '':
            data = self._completion_list
        else:
            data = [item for item in self._completion_list if value in item.lower()]
        self['values'] = data
        if data:
            self.after(
                700,
                lambda: self.event_generate('<Down>'),
            )
