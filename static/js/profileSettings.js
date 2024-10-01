const usernameField =document.querySelector('#username');
const feedbackArea=document.querySelector('.invalid_feedback');
const usernamesuccessOutput =document.querySelector('.usernameSuccessOutput');
const submitBtn = document.querySelector("#submitBtn");


usernameField.addEventListener('keyup',(e)=>{
          const usernameVal=e.target.value;
          usernamesuccessOutput.textContent= `Checking  ${usernameVal}`;
          usernamesuccessOutput.style.display="block";
          usernameField.classList.remove('is-invalid');
          feedbackArea.style.display='none';


          if(usernameVal.length>0){
                    fetch('/profileValidateUsername',{
                              body:JSON.stringify({username:usernameVal}),
                              method:'POST',
                    }).then(res=>res.json())
                    .then(data=>{
                              usernamesuccessOutput.style.display="none";
                              if(data.username_error){
                                        submitBtn.disabled=true;
                                        usernameField.classList.add('is-invalid');
                                        feedbackArea.style.display='block';
                                        feedbackArea.innerHTML = `<p>${data.username_error}</p>`;

                              }else{
                                        submitBtn.removeAttribute("disabled");
                              }
                    });

          }
          

});