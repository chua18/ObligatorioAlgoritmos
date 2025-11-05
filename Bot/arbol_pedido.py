class NodoPedido:
    def _init_(self, pedido):
        self.pedido = pedido
        self.izquierda = None
        self.derecha = None

class ArbolPedidos:
    def _init_(self):
        self.raiz = None

    def insertar(self, pedido):
        if not self.raiz:
            self.raiz = NodoPedido(pedido)
        else:
            self._insertar(self.raiz, pedido)

    def _insertar(self, nodo_actual, pedido):
        if pedido.distancia < nodo_actual.pedido.distancia:
            if nodo_actual.izquierda is None:
                nodo_actual.izquierda = NodoPedido(pedido)
            else:
                self._insertar(nodo_actual.izquierda, pedido)
        else:
            if nodo_actual.derecha is None:
                nodo_actual.derecha = NodoPedido(pedido)
            else:
                self._insertar(nodo_actual.derecha, pedido)

    def recorrido_inorden(self):
        pedidos = []
        self._inorden(self.raiz, pedidos)
        return pedidos

    def _inorden(self, nodo, pedidos):
        if nodo:
            self._inorden(nodo.izquierda, pedidos)
            pedidos.append(nodo.pedido)
            self._inorden(nodo.derecha, pedidos)

    def eliminar(self, codigo):
        self.raiz = self._eliminar(self.raiz, codigo)

    def _eliminar(self, nodo, codigo):
        if nodo is None:
            return nodo
        if codigo < nodo.pedido.codigo:
            nodo.izquierda = self._eliminar(nodo.izquierda, codigo)
        elif codigo > nodo.pedido.codigo:
            nodo.derecha = self._eliminar(nodo.derecha, codigo)
        else:
            if nodo.izquierda is None:
                return nodo.derecha
            elif nodo.derecha is None:
                return nodo.izquierda
            temp = self._min_value_node(nodo.derecha)
            nodo.pedido = temp.pedido
            nodo.derecha = self._eliminar(nodo.derecha, temp.pedido.codigo)
        return nodo

    def _min_value_node(self, nodo):
        actual = nodo
        while actual.izquierda is not None:
            actual = actual.izquierda
        return actual