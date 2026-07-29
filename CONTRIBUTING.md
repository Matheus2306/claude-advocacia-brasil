# Contribuição

## Princípios

- Manter cada skill focada em uma tarefa repetível.
- Escrever instruções em português claro e imperativo.
- Não incorporar dados internos ou casos identificáveis.
- Não reduzir os controles de verificação de fatos, fontes e prazos.
- Preservar revisão humana obrigatória.

## Alterações

1. Crie uma branch.
2. Altere apenas as skills necessárias.
3. Execute:

```bash
python scripts/validate_and_package.py
```

4. Teste prompts que devem e não devem acionar a skill.
5. Documente impacto e risco.
6. Abra pull request para revisão.

## Critérios de revisão

- O campo `description` indica claramente quando usar.
- Não há sobreposição desnecessária com outra skill.
- As fontes e exemplos não são inventados.
- O fluxo contém comportamento para informações faltantes.
- Prazos e cálculos exigem premissas.
- Referências relativas existem.
- A documentação acompanha mudanças funcionais.
