# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VectorStats
                                 A QGIS plugin
 Plugin for descriptive and statistical analysis of vectors, with chart generation
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-08-20
        git sha              : $Format:%H$
        email                : breno_1697@hotmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import os.path
from collections import defaultdict
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout
from qgis.core import QgsMapLayer, QgsProject
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from scipy.stats import linregress, mode

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the dialog
from .Stats_dialog import VectorStatsDialog


class VectorStats:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(
            self.plugin_dir, "i18n", "VectorStats_{}.qm".format(locale)
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr("&VectorStats")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        # Initialize figures and canvas as None
        self.fig = None
        self.canvas = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("VectorStats", message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/Stats/icon.png"
        self.add_action(
            icon_path,
            text=self.tr("VectorStats"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&VectorStats"), action)
            self.iface.removeToolBarIcon(action)

    def carregaVetor(self):
        """Fills the combox with the existing vector layers in the project"""
        self.dlg.layer.clear()
        lista_layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        lista_layer_vetor = []
        for layer in lista_layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                lista_layer_vetor.append(layer.name())
        self.dlg.layer.addItems(lista_layer_vetor)

    def carregaAtributos(self):
        """Fills the ComboBox with the attributes of the selected vector layer"""
        self.dlg.attributes.clear()
        layer_name = self.dlg.layer.currentText()
        layers = QgsProject.instance().mapLayersByName(layer_name)

        if not layers:
            self.iface.messageBar().pushMessage(
                "Erro", "Camada não encontrada.", level=3
            )
            return

        layer = layers[0]

        if layer.isValid():
            fields = layer.fields()
            attribute_names = [field.name() for field in fields]
            self.dlg.attributes.addItems(attribute_names)
        else:
            self.iface.messageBar().pushMessage("Erro", "Camada inválida.", level=3)

    def carregaAtributos2(self):
        """Fills the ComboBox with the attributes of the selected vector layer"""
        self.dlg.attributes_2.clear()
        layer_name = self.dlg.layer.currentText()
        layers = QgsProject.instance().mapLayersByName(layer_name)

        if not layers:
            self.iface.messageBar().pushMessage(
                "Erro", "Camada não encontrada.", level=3
            )
            return

        layer = layers[0]

        if layer.isValid():
            fields = layer.fields()
            attribute_names = [field.name() for field in fields]
            self.dlg.attributes_2.addItems(attribute_names)
        else:
            self.iface.messageBar().pushMessage("Erro", "Camada inválida.", level=3)

    def carregaAtributosX(self):
        """Fills the ComboBox with the attributes X of the selected vector layer"""
        self.dlg.layer_3.clear()
        layer_name = self.dlg.layer.currentText()
        layers = QgsProject.instance().mapLayersByName(layer_name)

        if not layers:
            self.iface.messageBar().pushMessage(
                "Erro", "Camada não encontrada.", level=3
            )
            return

        layer = layers[0]

        if layer.isValid():
            fields = layer.fields()
            attribute_names = [field.name() for field in fields]
            self.dlg.layer_3.addItems(attribute_names)
        else:
            self.iface.messageBar().pushMessage("Erro", "Camada inválida.", level=3)

    def carregaAtributosY(self):
        """Fills the ComboBox with the attribute Y of the selected vector layer."""
        self.dlg.layer_4.clear()
        layer_name = self.dlg.layer.currentText()
        layers = QgsProject.instance().mapLayersByName(layer_name)

        if not layers:
            self.iface.messageBar().pushMessage(
                "Erro", "Camada não encontrada.", level=3
            )
            return

        layer = layers[0]

        if layer.isValid():
            fields = layer.fields()
            attribute_names = [field.name() for field in fields]
            self.dlg.layer_4.addItems(attribute_names)
        else:
            self.iface.messageBar().pushMessage("Erro", "Camada inválida.", level=3)

    def extrairEstatisticas(self):
        """Extracts and displays the statistical values ​​of the selected attribute from the selected layer."""
        layer_name = self.dlg.layer.currentText()
        attribute_name = self.dlg.attributes.currentText()

        if not layer_name or not attribute_name:
            self.iface.messageBar().pushMessage(
                "Erro", "Por favor, selecione uma camada e um atributo.", level=3
            )
            return

        layer = QgsProject.instance().mapLayersByName(layer_name)[0]

        if not layer.isValid():
            self.iface.messageBar().pushMessage("Erro", "Camada inválida.", level=3)
            return

        values = []
        for feature in layer.getFeatures():
            value = feature[attribute_name]
            if isinstance(value, (int, float)):
                values.append(value)

        if not values:
            self.iface.messageBar().pushMessage(
                "Erro",
                "Nenhum valor numérico encontrado no atributo selecionado.",
                level=3,
            )
            return

        # Calculate statistics
        mean = round(np.mean(values), 2)
        median = round(np.median(values), 2)
        mode_value, _ = mode(values)
        mode_value = round(mode_value[0], 2)
        std_dev = round(np.std(values), 2)
        minimum = round(np.min(values), 2)
        maximum = round(np.max(values), 2)
        variance = round(np.var(values), 2)
        coefficient_of_variation = (
            round(std_dev / mean, 2) if mean != 0 else float("inf")
        )
        count = len(values)

        # Show results
        msg = (
            f"Estatísticas do atributo '{attribute_name}':\n\n"
            f"Média: {mean}\n\n"
            f"Mediana: {median}\n\n"
            f"Moda: {mode_value}\n\n"
            f"Desvio Padrão: {std_dev}\n\n"
            f"Mínimo: {minimum}\n\n"
            f"Máximo: {maximum}\n\n"
            f"Variância: {variance}\n\n"
            f"Coeficiente de Variação: {coefficient_of_variation}\n\n"
            f"Contagem: {count}"
        )
        # self.iface.messageBar().pushMessage("Estatísticas", msg, level=1)
        # Display the message in QTextEdit
        self.dlg.outputTextEdit.setPlainText(msg)

    def extrairEstatisticas2(self):
        """Extracts and displays the statistical values ​​of the selected attribute from the selected layer"""
        layer_name = self.dlg.layer.currentText()
        attribute_name = self.dlg.attributes_2.currentText()

        if not layer_name or not attribute_name:
            self.iface.messageBar().pushMessage(
                "Erro", "Por favor, selecione uma camada e um atributo.", level=3
            )
            return

        layer = QgsProject.instance().mapLayersByName(layer_name)[0]

        if not layer.isValid():
            self.iface.messageBar().pushMessage("Erro", "Camada inválida.", level=3)
            return

        values = []
        for feature in layer.getFeatures():
            value = feature[attribute_name]
            if isinstance(value, (int, float)):
                values.append(value)

        if not values:
            self.iface.messageBar().pushMessage(
                "Erro",
                "Nenhum valor numérico encontrado no atributo selecionado.",
                level=3,
            )
            return

        # Calculate statistics
        mean = round(np.mean(values), 2)
        median = round(np.median(values), 2)
        mode_value, _ = mode(values)
        mode_value = round(mode_value[0], 2)
        std_dev = round(np.std(values), 2)
        minimum = round(np.min(values), 2)
        maximum = round(np.max(values), 2)
        variance = round(np.var(values), 2)
        coefficient_of_variation = (
            round(std_dev / mean, 2) if mean != 0 else float("inf")
        )
        count = len(values)

        # Show results
        msg = (
            f"Estatísticas do atributo '{attribute_name}':\n\n"
            f"Média: {mean}\n\n"
            f"Mediana: {median}\n\n"
            f"Moda: {mode_value}\n\n"
            f"Desvio Padrão: {std_dev}\n\n"
            f"Mínimo: {minimum}\n\n"
            f"Máximo: {maximum}\n\n"
            f"Variância: {variance}\n\n"
            f"Coeficiente de Variação: {coefficient_of_variation}\n\n"
            f"Contagem: {count}"
        )
        # self.iface.messageBar().pushMessage("Estatísticas", msg, level=1)
        # Display the message in QTextEdit
        self.dlg.outputTextEdit_2.setPlainText(msg)

    def tipo_grafico(self):
        """fills the ComboBox with the types of graphs that can be generated"""
        self.dlg.layer_5.clear()
        lista_graficos = [
            "Histograma",
            "Barras (eixo X = Categórico; eixo Y = Numérico; métrica = Soma)",
            "Barras (eixo X = Categórico; eixo Y = Numérico; métrica = Média)",
            "Dispersão",
            "Série Histórica (eixo X= Data; eixo Y= Numérico, métrica = Média)",
            "Série Histórica (eixo X= Data; eixo Y= Numérico, métrica = Soma)",
        ]
        self.dlg.layer_5.addItems(lista_graficos)

    def gerar_grafico(self):
        """Generates a graph based on the selected layer, X and Y attributes, and graph type."""
        layer_name = self.dlg.layer.currentText()
        attribute_x = self.dlg.layer_3.currentText()
        attribute_y = self.dlg.layer_4.currentText()
        tipo_grafico = self.dlg.layer_5.currentText()

        if not layer_name or not attribute_x or not attribute_y:
            self.iface.messageBar().pushMessage(
                "Erro", "Por favor, selecione uma camada e os atributos X e Y.", level=3
            )
            return

        layer = QgsProject.instance().mapLayersByName(layer_name)[0]

        if not layer.isValid():
            self.iface.messageBar().pushMessage("Erro", "Camada inválida.", level=3)
            return

        values_x = []
        values_y = []
        for feature in layer.getFeatures():
            value_x = feature[attribute_x]
            value_y = feature[attribute_y]
            if isinstance(value_y, (int, float)):
                values_x.append(value_x)  # Converter value_x para string
                values_y.append(value_y)

        if not values_x or not values_y:
            self.iface.messageBar().pushMessage(
                "Erro",
                "Nenhum valor numérico encontrado nos atributos selecionados.",
                level=3,
            )
            return

        # Create figure and axes
        if tipo_grafico == "Histograma":
            # Create a figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 6))

            # Histogram for X axis
            ax1.hist(values_x, bins=20, color="blue", alpha=0.7)
            ax1.set_title(f"Histograma: {attribute_x}")
            ax1.set_xlabel(attribute_x)
            ax1.set_ylabel("Frequência")

            # Histogram for Y axis
            ax2.hist(values_y, bins=20, color="green", alpha=0.7)
            ax2.set_title(f"Histograma: {attribute_y}")
            ax2.set_xlabel(attribute_y)
            ax2.set_ylabel("Frequência")

            # Adjust layout
            plt.tight_layout()
            self.fig = fig
            self.ax = (ax1, ax2)
        elif tipo_grafico == "Dispersão":
            self.fig, self.ax = plt.subplots()
            self.ax.scatter(values_x, values_y, s=10)
            self.ax.set_title(f"Gráfico de Dispersão: {attribute_x} vs {attribute_y}")
            self.ax.set_xlabel(attribute_x)
            self.ax.set_ylabel(attribute_y)

            # Calculate the coefficient of determination (R²)
            slope, intercept, r_value, p_value, std_err = linregress(values_x, values_y)
            r_squared = r_value**2

            # Display the R² value on the plot
            self.ax.text(
                0.05,
                0.95,
                f"$R^2 = {r_squared:.2f}$",
                transform=self.ax.transAxes,
                fontsize=12,
                verticalalignment="top",
            )
        elif (
            tipo_grafico
            == "Série Histórica (eixo X= Data; eixo Y= Numérico, métrica = Média)"
        ):
            # Convert x_values ​​(QDate) to strings
            def parse_date(date_str):
                for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Date format for {date_str} is not supported")

            # Filtrar valores nulos e converter datas válidas
            date_strings = [
                parse_date(date.toString("yyyy-MM-dd")).strftime("%d-%m-%Y")
                for date in values_x
                if date is not None and date.isValid()
            ]

            values_y_filtered = [
                value
                for date, value in zip(values_x, values_y)
                if date is not None and date.isValid()
            ]

            df = pd.DataFrame({"date": date_strings, "value": values_y_filtered})
            df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

            df_mean = df.groupby("date").mean().reset_index()
            dates = mdates.date2num(df_mean["date"].to_list())
            y_mean_values = df_mean["value"].to_list()

            self.fig, self.ax = plt.subplots()
            self.ax.plot_date(
                dates,
                y_mean_values,
                linestyle="solid",
                label="Média da Série Histórica",
            )

            self.ax.set_title(f"Série Histórica: Média de {attribute_y}")
            self.ax.set_xlabel(attribute_x)
            self.ax.set_ylabel(f"Média de {attribute_y}")

            # Format the X axis to display dates legibly
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())

            # Rotate date labels for better readability
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")
            self.ax.legend()
            self.fig.tight_layout()

        elif (
            tipo_grafico
            == "Série Histórica (eixo X= Data; eixo Y= Numérico, métrica = Soma)"
        ):
            # Convert x_values ​​(QDate) to strings
            def parse_date(date_str):
                for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Date format for {date_str} is not supported")

            date_strings = [
                parse_date(date.toString("yyyy-MM-dd")).strftime("%d-%m-%Y")
                for date in values_x
                if date is not None and date.isValid()
            ]

            values_y_filtered = [
                value
                for date, value in zip(values_x, values_y)
                if date is not None and date.isValid()
            ]

            df = pd.DataFrame({"date": date_strings, "value": values_y_filtered})
            df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
            df_sum = df.groupby("date").sum().reset_index()

            # Convert dates to Matplotlib numeric format
            dates = mdates.date2num(df_sum["date"].to_list())
            y_sum_values = df_sum["value"].to_list()

            self.fig, self.ax = plt.subplots()
            self.ax.plot_date(
                dates,
                y_sum_values,
                linestyle="solid",
                label="Soma da Série Histórica",
            )

            self.ax.set_title(f"Série Histórica: Soma de {attribute_y}")
            self.ax.set_xlabel(attribute_x)
            self.ax.set_ylabel(f"Soma de {attribute_y}")

            # Format the X axis to display dates legibly
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())

            # Rotate date labels for better readability
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")
            self.ax.legend()
            self.fig.tight_layout()
        elif (
            tipo_grafico
            == "Barras (eixo X = Categórico; eixo Y = Numérico; métrica = Soma)"
        ):
            # Group numerical values ​​by category and calculate the sum
            category_sums = defaultdict(float)
            for x, y in zip(values_x, values_y):
                category_sums[str(x)] += y

            # Prepare data for the chart
            categories = list(category_sums.keys())
            sums = list(category_sums.values())

            # Generate the bar chart
            self.fig, self.ax = plt.subplots()
            self.ax.bar(categories, sums)
            self.ax.set_title(
                f"Gráfico de Barras Categóricas: {attribute_x} vs {attribute_y}"
            )
            self.ax.set_xlabel(attribute_x)
            self.ax.set_ylabel(f"Soma de {attribute_y}")
        elif (
            tipo_grafico
            == "Barras (eixo X = Categórico; eixo Y = Numérico; métrica = Média)"
        ):
            # Group numerical values ​​by category and calculate the average
            category_sums = defaultdict(float)
            category_counts = defaultdict(int)
            for x, y in zip(values_x, values_y):
                category_sums[str(x)] += y
                category_counts[x] += 1

            # Calculate the average for each category
            category_means = {
                k: category_sums[k] / category_counts[k] for k in category_sums
            }

            # Prepare data for the chart
            categories = list(category_means.keys())
            means = list(category_means.values())

            # Generate the bar chart
            self.fig, self.ax = plt.subplots()
            self.ax.bar(categories, means)
            self.ax.set_title(
                f"Gráfico de Barras Categóricas: {attribute_x} vs {attribute_y}"
            )
            self.ax.set_xlabel(attribute_x)
            self.ax.set_ylabel(f"Média de {attribute_y}")
        else:
            self.iface.messageBar().pushMessage(
                "Erro", "Tipo de gráfico desconhecido.", level=3
            )
            return

        # Clear previous layout
        for i in reversed(range(self.dlg.graphLayout.count())):
            self.dlg.graphLayout.itemAt(i).widget().setParent(None)

        # Add the canvas to the layout
        self.canvas = FigureCanvas(self.fig)
        self.dlg.graphLayout.addWidget(self.canvas)

    def salvar_grafico(self):
        """Salve the generated graph to a file."""
        if self.fig is None:
            self.iface.messageBar().pushMessage(
                "Erro", "Nenhum gráfico gerado para salvar.", level=3
            )
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self.dlg,
            "Salvar Gráfico",
            "",
            "PNG Files (*.png);;All Files (*)",
            options=options,
        )
        if file_path:
            self.fig.savefig(file_path)

    def update_attributes(self):
        """Updates attributes based on combo_box selection."""
        selected_layer = self.dlg.layer.currentText()
        if selected_layer == "layer_2":
            self.carregaAtributosX = "novo_valor_X"
            self.carregaAtributosY = "novo_valor_Y"
            print(
                f"carregaAtributosX: {self.carregaAtributosX}, carregaAtributosY: {self.carregaAtributosY}"
            )

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = VectorStatsDialog()

            # Connect the Layer ComboBox selection change signal to the LoadAttributes function
            self.dlg.layer.currentIndexChanged.connect(self.carregaAtributos)
            self.dlg.layer.currentIndexChanged.connect(self.carregaAtributos2)
            self.dlg.layer.currentIndexChanged.connect(self.carregaAtributosX)
            self.dlg.layer.currentIndexChanged.connect(self.carregaAtributosY)

            # Connect selection change events
            self.dlg.layer.currentIndexChanged.connect(self.update_attributes)

            # Connect the calculation button to the extractStatistics function
            self.dlg.calculateButton.clicked.connect(self.extrairEstatisticas)
            self.dlg.calculateButton.clicked.connect(self.extrairEstatisticas2)

            # Connect the generic graph button to the generate_graph function
            self.dlg.graphButton.clicked.connect(self.gerar_grafico)

            # Connect the save graph button to the save_graph function
            self.dlg.saveGraphButton.clicked.connect(self.salvar_grafico)

        # show the dialog
        self.dlg.show()
        self.carregaVetor()
        self.carregaAtributos()
        self.carregaAtributos2()
        self.carregaAtributosX()
        self.carregaAtributosY()
        self.tipo_grafico()

        # Configure the layout for the chart
        self.dlg.graphLayout = QVBoxLayout(self.dlg.graphWidget)
        self.dlg.graphWidget.setLayout(self.dlg.graphLayout)

        # show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
