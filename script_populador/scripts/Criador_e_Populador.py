#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 13:18:01 2025

@author: pablo
"""

import criacao_banco as cb
import funcoes_populacao as fp

usuario = 'postgres'
senha = '123'
host = 'localhost'
porta = '5432'
banco = 'loja_vendas'

qtd_clientes = 200 # altere para quantos quiser
qtd_pedidos = 1000 # altere para quantos quiser

engine = cb.main(usuario, senha, host, porta, banco)
fp.main(engine, qtd_clientes, qtd_pedidos)
