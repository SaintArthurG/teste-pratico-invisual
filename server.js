const { json } = require('body-parser');
const express = require('express')
const xlsx = require('node-xlsx').default
const fs = require('fs')


const PORTA = 3000;

const app = express();

app.use(json())

app.post('/filmes', (req, res)=>{
    const filmesData  = req.body;
    console.log(filmesData);
    

    let arrayDeFilmes = filmesData.map(filme => [
        filme.titulo,
        filme.ano,
        filme.duracao,
        filme.nota,
        filme.sinopse])

    var buffer = xlsx.build([{
        name: 'filmesxl', data: arrayDeFilmes
    }]);

    try{
        fs.writeFileSync('filmes.xlsx', buffer)
        res.status(200).json({
            messagem: "Planilha criada com sucesso!"
        })
    } catch(e) {
        res.status(400).json({
            error: "Falha ao criar a planilha " + e
        })
    }
})

app.listen(PORTA, ()=>{
    console.log(`Servidor rodando na porta ${PORTA}`);
})