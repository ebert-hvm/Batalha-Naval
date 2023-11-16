# Batalha-Naval
Implementação do jogo Batalha Naval em python

## Instalação
O programa utiliza a bilbioteca pygame não padrão. Para instalar, rode o código no terminal:

```pip install pygame```

## Configuração

É possível configurar a dimensão do tabuleiro, número de navios, e seus tamanhos pelo arquivo ```configurations.json```.

Nesse mesmo arquivo, deve-se modificar o endereço IP do server para a máquina que irá ser host: ```"server" : {
        "ip": "<IP>" }```

## Rodar
Caso seja servidor, rode o comando em um terminal:

```python server.py```

Caso seja jogador, rode o comando em um terminal:

```python main.py```

É possível rodar todos os 3 (2 jogadores e 1 servidor) em uma única máquina abrindo 3 terminais.