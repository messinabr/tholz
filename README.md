# Tholz LuxPool para Home Assistant

Integração personalizada para controlar pelo Home Assistant os controladores de piscina da **Tholz**, como o **Trocador de Calor LuxPool**, direto pela rede local (Wi-Fi), sem nuvem.

> Projeto não oficial, sem vínculo com a Tholz. Use por sua conta e risco.

## O que ela faz

A integração conversa com o controlador pela rede local (TCP, porta 4000, mensagens JSON) e cria um único dispositivo, **Tholz Controlador**, com as entidades abaixo.

### Aquecimento

| Entidade | Tipo | Descrição |
|---|---|---|
| Aquecedor | `climate` | Liga e desliga o aquecimento (modo Aquecer) e define a temperatura-alvo, de 18 a 40 °C, em passos de 1 °C. Também alterna o ventilador entre **Silencioso** e **Inteligente**. |
| Aquecendo Agora | `binary_sensor` | Indica se o trocador está aquecendo neste momento. |

### Sensores

| Entidade | Descrição |
|---|---|
| Temperatura Piscina | Temperatura da água da piscina (sensor T3), usada como temperatura atual do Aquecedor. |
| Temperatura Saída Trocador | Temperatura da água na saída do trocador (T2). |
| Temperatura Ambiente | Temperatura do ar (T1). |
| Status | Estado do equipamento: `Normal` ou a descrição do erro, como Falta de Água, Baixo fluxo de água ou Pressão Alta. |
| Modelo | Modelo reconhecido do controlador. |
| Firmware | Versão do firmware. |

### Saídas, iluminação e ajustes

Estas entidades são criadas **conforme o que o seu controlador informa**. Se o seu modelo não tem determinada saída ou LED, ela simplesmente não aparece.

| Entidade | Tipo | Descrição |
|---|---|---|
| Saídas (Filtro, Apoio Elétrico, Apoio a Gás, Recirculação, Borbulhador, Circulação, Auxiliar, Cascata, Hidro, Interruptor) | `switch` | Liga e desliga cada saída do controlador. |
| LED | `light` | Liga e desliga, brilho, cor RGB e efeitos. |
| Velocidade LED | `number` | Velocidade do efeito do LED, de 0 a 100. |
| Fuso Horário | `select` | Ajusta o fuso horário do controlador. Aparece só se o equipamento informar essa configuração. |

## Requisitos

- Home Assistant **2024.1.0** ou superior.
- [HACS](https://hacs.xyz/) instalado (ou instalação manual, descrita abaixo).
- Controlador Tholz conectado ao Wi-Fi, na mesma rede do Home Assistant.
- Recomendado: **IP fixo** (reserva de DHCP no roteador) para o controlador, já que a integração se identifica pelo IP.

## Instalação

### Pelo HACS (recomendado)

1. No Home Assistant, abra **HACS**.
2. Clique no menu ⋮ no canto superior direito e escolha **Repositórios personalizados**.
3. Cole `https://github.com/messinabr/tholz`, selecione a categoria **Integração** e clique em **Adicionar**.
4. Procure por **Tholz LuxPool** no HACS e clique em **Baixar**.
5. **Reinicie o Home Assistant.**

### Manual

1. Baixe este repositório.
2. Copie a pasta `custom_components/tholz` para dentro da pasta `custom_components` da sua configuração (normalmente `/config/custom_components/tholz`).
3. **Reinicie o Home Assistant.**

## Configuração

1. Vá em **Configurações → Dispositivos e serviços → Adicionar integração**.
2. Procure por **Tholz LuxPool**.
3. Informe o **endereço IP** do seu controlador Tholz e confirme.

O dispositivo **Tholz Controlador** aparece com todas as entidades. Para adicionar o aquecedor a um painel, use um cartão **Termostato** com a entidade `climate` **Aquecedor**.

## Modelos reconhecidos

A integração reconhece estes modelos pelo ID informado pelo controlador: LuxPool, TurboSilence, THC30/45/60/80, SmartPlus, SmartPool, Basic SmartPool, SmartHeat, Basic SmartHeat, TLZ Smart, TLS Smart e SmartLux.

O desenvolvimento e os testes foram feitos com o **Trocador de Calor LuxPool**. Os demais modelos usam o mesmo protocolo, mas não foram testados. Se o seu modelo aparecer como "Desconhecido", abra uma issue com o ID mostrado.

## Como funciona

- Toda a comunicação é **local**: nada passa pela internet.
- O controlador atende **uma conversa por vez**. A integração enfileira as requisições e, se o equipamento estiver ocupado, tenta de novo até 3 vezes antes de marcar falha.
- Os dados são lidos por *polling* periódico; comandos enviados pelo Home Assistant são aplicados no controlador na hora.

## Limitações conhecidas

- Os **efeitos de LED** têm nomes genéricos (Cor Fixa, Efeito 0, 1 e 2), porque os nomes originais ainda não foram mapeados.
- A tabela de **códigos de erro** é parcial; códigos fora dela aparecem como "Erro desconhecido (N)".
- O controle de aquecimento usa o primeiro circuito de aquecimento do controlador (`heat0`).

## Solução de problemas

**Aparecem dois dispositivos "Tholz Controlador", um deles cinza e desabilitado**

Isso acontece quando uma versão antiga da integração registrou o dispositivo com outro identificador. Para limpar:

1. Atualize a integração para a versão mais recente e reinicie o Home Assistant.
2. Abra o dispositivo duplicado (o cinza), apague as entidades indisponíveis dele, se houver.
3. No menu ⋮ do dispositivo, clique em **Excluir**. A integração só libera a exclusão de dispositivos que não sejam o atual.

**Entidades ficam "indisponíveis"**

- Confirme que o IP do controlador não mudou e que ele responde na rede.
- Verifique se há outro aplicativo conectado ao controlador ao mesmo tempo.
- Ative o log detalhado em `configuration.yaml` e veja as mensagens:

```yaml
logger:
  logs:
    custom_components.tholz: debug
```

## Contribuindo

Encontrou um bug, tem um modelo diferente ou sabe os nomes dos efeitos de LED? Abra uma [issue](https://github.com/messinabr/tholz/issues) ou envie um pull request.
