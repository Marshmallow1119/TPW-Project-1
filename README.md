# TPW - Projeto 1 - Descrição e Funcionalidades

## Merchify

#

## Introdução ao tema

Neste primeiro projeto desenvolvemos uma aplicação web usando a framework Django. A aplicação chama-se Merchify e consiste numa plataforma online de venda de merchandising exclusivo de diversos artistas. A interface possui várias páginas que permitem ao utilizador navegar de forma eficiente e intuitiva. Todos os produtos estão numa página específica, sendo que estão apresentados de forma clara e categorizados por artistas, facilitando a busca por itens do artista favorito do utilizador. Para além das funcionalidades oferecidas pelo Django, usamos HTML, CSS e JS para garantir que a página tem um design atrativo e responsivo. Por fim, os utilizadores podem adicionar os produtos ao carrinho e completar a compra de maneira simples e rápida.

## Principais Funcionalidades da Aplicação

### Django Frameworks utilizadas:

- Forms - adição e edição de produtos e empresas
- Sessions - quando o cliente vê produtos, aparecem numa aba de visualizados recentemente
- Authentication - login e logout dos 3 tipos de utilizadores

### Utilizador sem login realizado

- Fazer pesquisa de produtos e de artistas
- Login
- Registo
- Ver os Artistas
- Ver os Produtos e os seus detalhes

### Utilizador com login realizado

- Logout
- Pesquisar por produto
- Pesquisar por artistas
- Adicionar produtos aos favoritos
- Adicionar artistas aos favoritos
- Ver os produtos e os artistas que foram colocados como favoritos
- Ver produtos e os seus detalhes
- Ver os produtos de um determinado artista
- Ver/ atualizar/ apagar dados do perfile
- Ver encomendas e os seus detalhes
- Comprar um produto
- Adicionar um avaliação a um produto
- Receber um desconto de 10% na primeira compra com o código "PRIMEIRACOMPRA"
- Encomendas com portes grátis em compras superiores a 100€
- Encomendas com portes mais baratos se o seu país for Portugal
- Ver os últimos 4 produtos vistos recentemente

### Admin

- O mesmo que o utilizador com login
- Ver o número de compras de um utilizador
- Adicionar Companhias
- Banir Companhias
- Adicionar Produtos
- Editar Produtos
- Adicionar Stock a um Produto
- Ver o número de avaliações e a média de avaliações de um produto
- Remover Produtos
- Apagar Avaliações

### Empresa

- O mesmo que o utilizador com login
- Ver dados sobre os próprios produtos
- Adicionar produtos
- Editar produtos
- Remover produtos
- Adicionar stock a um produto
- Ver dados sobre os próprios produtos
- Ver as avaliações médias dos seus produtos
- Ver o número de favoritos dos seus produtos

## Funcionalidades que poderiamos implementar no futuro

- Sistema de Recomendações
- Sistema de Chat
- Sistema de Notificações
- Promoções específicas para cada produto

## Informação de autenticação de users;

<table>
<th>
<td>Username</td>
<td>Password</td>
</th>
<tr>
<td>Administrador</td>
<td>admin</td>
<td>admin123</td>
</tr>
<tr>
<td>Cliente</td>
<td>joao1</td>
<td>testaruser123</td>
</tr>
<tr>
<td>Empresas</td>
<td>republic</td>
<td>republic123</td>
</tr>
</table>

## Algumas funcionalidades Django usadas e onde foram usadas:

- **DjangoModel** - Usámos para criar as tabelas da base de dados, como por exemplo, a tabela de utilizadores, produtos, artistas, encomendas, etc.
- **DjangoViews** - Usámos para criar as views das páginas, como por exemplo, a página de login, registo, ver produtos, ver artistas, etc.
- **DjangoTemplates** - Usámos para criar as páginas HTML, como por exemplo, a página de login, registo, ver produtos, ver artistas, etc.
- **DjangoTemplatesTags** - Usámos para criar tags personalizadas, como por exemplo, a tag que calcula o preço total de uma encomenda.
- **DjangoSessions** - Usámos para guardar os produtos que o utilizador viu recentemente.
- **DjangoMiddleware** - Usámos para redirecionar o utilizador para uma página de erro default caso o utilizador tente aceder a uma página que não existe.
- **DjangoForms** - Usámos para criar formulários de registo, login, atualização de perfil, adicionar produtos, adicionar companhias, adicionar avaliações.

## Deployment (PythonAnyWhere)

https://alof.pythonanywhere.com/

## Conclusão

Para concluir, o projeto Merchify foi bastante enriquecedor para todos os membros. Aprendemos a trabalhar com Django e a desenvolver uma aplicação web de raiz. A aplicação desenvolvida é bastante completa e oferece várias funcionalidades que permitem ao utilizador ter uma experiência agradável e intuitiva. À medida que fomos desenvolvendo a aplicação, fomos ganhando mais ideias, sempre com o objetivo de melhorar a experiência do utilizador. A aplicação Merchify é um projeto que nos orgulha e que nos deu a oportunidade de aplicar os conhecimentos adquiridos sobre Django.
