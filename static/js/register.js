const usernameField=document.querySelector('#usernameField');
const feedbackArea=document.querySelector('.invalid_feedback');
const emailFeedbackArea=document.querySelector('.emailFeedbackArea');
const emailField=document.querySelector('#emailField');
const usernamesuccessOutput=document.querySelector('.usernamesuccessOutput');
const emailsuccessOutput=document.querySelector('.emailsuccessOutput');
const showPasswordToggle=document.querySelector('.showPasswordToggle');
const passwordField=document.querySelector('#passwordField');
const submitBtn=document.querySelector('#signup');

const handleToggleInput=(e)=>{
          if (showPasswordToggle.textContent==='Show Password'){
                    showPasswordToggle.textContent="Hide Password";
                    passwordField.setAttribute('type','text');
          }
          else{
                    showPasswordToggle.textContent="Show Password";
                    passwordField.setAttribute('type','password');


          }

}


showPasswordToggle.addEventListener('click',handleToggleInput);


emailField.addEventListener('keyup',(e)=>{
          const emailVal=e.target.value;
          emailsuccessOutput.textContent= `Checking  ${emailVal}`;
          emailsuccessOutput.style.display="block";
          emailField.classList.remove('is-invalid');
          emailFeedbackArea.style.display="none";
          if(emailVal.length>0){
                    fetch('/validateUserEmail',{
                              body:JSON.stringify({email:emailVal}),
                              method:'POST',
                    }).then(res=>res.json())
                    .then(data=>{
                              emailsuccessOutput.style.display="none";
                              if(data.email_error){
                                        submitBtn.disabled=true;
                                        emailField.classList.add('is-invalid');
                                        emailFeedbackArea.style.display="block";
                                        emailFeedbackArea.innerHTML = `<p>${data.email_error}</p>`;

                              }else{
                                        submitBtn.removeAttribute("disabled");
                              }
                    });

          }
          

});


usernameField.addEventListener('keyup',(e)=>{
          const usernameVal=e.target.value;
          usernamesuccessOutput.textContent= `Checking  ${usernameVal}`;
          usernamesuccessOutput.style.display="block";
          usernameField.classList.remove('is-invalid');
          feedbackArea.style.display='none';

          if(usernameVal.length>0){
                    fetch('/validateUserName',{
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

