# Instalação

## Requisitos

- Conta Claude Free, Pro, Max, Team ou Enterprise com Skills disponíveis.
- **Code execution and file creation** habilitado.
- Um ZIP por skill, gerado pela versão atual deste repositório.

## Claude Web

1. Acesse `https://claude.ai/`.
2. Em contas individuais, abra **Settings > Capabilities**.
3. Ative **Code execution and file creation**.
4. Abra **Customize > Skills**.
5. Clique em **+ > Create skill > Upload a skill**.
6. Selecione um ZIP da pasta `dist/`.
7. Ative a skill e repita para as demais.

## Claude Desktop

1. Atualize o aplicativo.
2. Entre na mesma conta utilizada no navegador.
3. Confirme que a capacidade de execução e arquivos está ativa.
4. Abra **Customize > Skills**.
5. Envie e ative os ZIPs.

As skills habilitadas na conta ficam disponíveis no chat Web e no Desktop. A interface pode variar conforme plano, sistema operacional e versão.

## Team e Enterprise

Um proprietário da organização pode:

- provisionar uma skill para todos;
- compartilhar skills na organização;
- agrupar skills em plugin e atribuir a grupos específicos.

Antes da distribuição:

1. teste em uma conta controlada;
2. revise segurança e sigilo;
3. aprove a versão;
4. registre responsável e data;
5. mantenha procedimento de rollback.

## Atualização

Skills instaladas manualmente não devem ser presumidas como sincronizadas com o GitHub. Ao publicar uma versão:

1. gere novos ZIPs;
2. registre alterações;
3. teste;
4. substitua a skill no Claude;
5. confirme o comportamento com prompts de validação.

## Problemas frequentes

### A skill não aparece

- Confirme que Code execution está habilitado.
- Verifique se o ZIP contém a pasta da skill e, dentro dela, `SKILL.md`.
- Confirme que pasta e campo `name` possuem o mesmo nome.

### A skill não é acionada

- Verifique se ela está ativada.
- Peça explicitamente: “Use a skill `nome-da-skill`”.
- Revise a descrição do frontmatter para evitar sobreposição.

### A skill de prazos não lembra tarefas

Abra um Projeto/Cowork com `controle-de-prazos.md` ou anexe o arquivo na conversa. Uma conversa sem estado persistente não garante memória entre sessões.
