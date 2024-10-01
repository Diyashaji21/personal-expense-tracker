const searchField=document.querySelector('#searchInput');
const appTable=document.querySelector('.app-table');
const tableOutput=document.querySelector('.table-output');
const paginationContainer=document.querySelector('.pagination-container')
const tbody=document.querySelector('.table-body')

tableOutput.style.display='none';

searchField.addEventListener('keyup',(e)=>{
          const searchValue=e.target.value;
          if(searchValue.trim().length>0){
                    paginationContainer.style.display='none';
                    tbody.innerHTML=''
                    fetch('/searchIncome',{
                              body:JSON.stringify({searchText:searchValue}),
                              method:'POST',
                    }).then(res=>res.json())
                    .then(data=>{
                              console.log("data",data);
                              tableOutput.style.display='block';
                              appTable.style.display='none';
                              if(data.length===0){
                                        tableOutput.innerHTML='No results found'

                              }else{
                                        data.forEach(item=>{
                                                  tbody.innerHTML+=`
                                                  <tr>
                                                  <td>${item.amount}</td>
                                                  <td>${item.date}</td>
                                                  <td>${item.source}</td>
                                                  <td>${item.description}</td>
                                                  <td><a href="/editIncome/${item.id}" class="btn btn-secondary">Edit</a>
                                                      <a href="/deleteIncome/${item.id}" class="btn btn-danger">Delete</a>
                                                  </td>
                                                  </tr>`   
                                        });
                                        
                                       
                              }
                    });
          }else{
                    tableOutput.style.display='none';
                    appTable.style.display='block';
                    paginationContainer.style.display='block';
          }
})