# Instalação

O repositório distribui as dez skills como um único plugin chamado **Advocacia Brasil**. Também gera pacotes individuais para contas que aceitam somente upload de skills.

## Claude Code — marketplace pelo GitHub

O repositório é privado. Antes de instalar, confirme que o Git usado pelo Claude Code possui acesso a `Matheus2306/claude-advocacia-brasil`.

Dentro do Claude Code:

```text
/plugin marketplace add Matheus2306/claude-advocacia-brasil
/plugin install advocacia-brasil@advocacia-brasil-marketplace
/reload-plugins
```

Teste uma skill:

```text
/advocacia-brasil:pesquisa-juridica-brasileira
```

Para atualizar:

```text
/plugin marketplace update advocacia-brasil-marketplace
```

Depois, confirme a versão do plugin no gerenciador `/plugin`.

## Teste local no Claude Code

Na pasta do repositório:

```bash
claude plugin validate .
claude plugin validate ./plugins/advocacia-brasil
claude --plugin-dir ./plugins/advocacia-brasil
```

## Claude Web e Desktop — Team ou Enterprise

O proprietário da organização pode criar um marketplace interno:

1. Habilite **Cowork** e **Skills** na organização.
2. Abra **Organization settings > Plugins**.
3. Selecione **Add plugin > GitHub**.
4. Informe `Matheus2306/claude-advocacia-brasil`.
5. Confirme que o Claude GitHub App tem acesso ao repositório.
6. Aguarde a sincronização e defina a preferência do plugin:
   - disponível para instalação;
   - instalado por padrão;
   - obrigatório;
   - não disponível.

O repositório usado na sincronização organizacional deve permanecer privado ou interno. A atualização pode ser manual ou automática, conforme as permissões configuradas.

## Upload manual do plugin

Gere os pacotes:

```bash
python scripts/validate_and_package.py
```

Envie `dist/advocacia-brasil.zip` ao marketplace da organização em **Organization settings > Plugins > Add plugins > Upload a file**.

O pacote deve ter menos de 50 MB. Um novo upload com o mesmo nome substitui a versão anterior.

## Contas com upload individual de skills

Quando a interface disponibilizar **Customize > Skills > Upload a skill**, use os dez ZIPs individuais de `dist/`, ignorando `advocacia-brasil.zip`.

As skills associadas à conta ficam disponíveis no Claude Web e Desktop conforme o plano e as capacidades habilitadas.

## Atualização e versionamento

Ao publicar uma versão:

1. altere `version` em `.claude-plugin/marketplace.json`;
2. altere a mesma versão em `plugins/advocacia-brasil/.claude-plugin/plugin.json`;
3. valide e gere os pacotes;
4. publique as alterações;
5. atualize ou sincronize o marketplace;
6. execute os prompts de teste.

## Problemas frequentes

### Marketplace não carrega

- Confirme a existência de `.claude-plugin/marketplace.json`.
- Verifique o acesso ao repositório privado.
- Execute `claude plugin validate .`.

### Plugin aparece, mas as skills não

- Confirme que as pastas estão em `plugins/advocacia-brasil/skills/`.
- Execute `/reload-plugins`.
- Verifique os erros no gerenciador `/plugin`.

### A skill de prazos não lembra tarefas

Abra um Projeto ou Cowork com `controle-de-prazos.md`, ou anexe o arquivo na conversa. Uma conversa sem estado persistente não garante memória entre sessões.
