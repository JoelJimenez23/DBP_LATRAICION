// form_loginId
const pendingForms = new WeakMap()


// function login_acces(){
//     const form_loginId = document.querySelector('#form_loginId',)
//     form_loginId.addEventListener('submit',handlinLoginUser)
// }

// function handlinLoginUser(e){
//     e.preventDefault()
//     e.stopPropagation()
    
//     const form_login = e.currentTarget
//     const previousController = pendingForms.get(form_login)
//     if(previousController){
//         previousController.abort()
//     }
//     const controller = new AbortController()
//     pendingForms.set(form_login,controller)

//     const formData = new FormData(form_login)

//     fetch('/teoria',{
//         method:'POST',
//         body:formData,
//         signal: controller.signal,
//     }).then((response) => response.json()).then((responseJson) =>{
//         if(responseJson.success){
//             window.location.href = "http://127.0.0.1:5000/market";
//         }
//         else{
//             const errorLoginMessage = document.getElementById('errorLoginMessage',)
//             errorLoginMessage.style.display = 'block'
//             setTimeout(() => {
//                 form_login.reset()
//                 errorLoginMessage.style.display = 'none'
//             },3000)
//         }
//     })
// }
