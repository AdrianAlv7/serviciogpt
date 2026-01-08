document.addEventListener('DOMContentLoaded', function() {
  (function() {
    // 缓存DOM元素（更精确的选择器）
    const DOM = {
      loginTabs: document.querySelectorAll('.login-items li'),
      forms: document.querySelectorAll('.forms-container > .login-datos'),
      formsContainer: document.querySelector('.forms-container'),
      loginItems: document.querySelector('.login-items'),
      identificar: document.querySelector('.identificar'),
      loginButtons: document.querySelectorAll('.forms-container .boton'),
      identificacionForm: document.querySelector('.identificacion-form'),
      toggleIdentificar: document.getElementById('toggle-identificar'),
      volverLogin: document.getElementById('volver-login'),
      submitIdentificacion: document.getElementById('submit-identificacion'),
      fileInput: document.querySelector('.identificacion-form input[type="file"]'),
      fileNameDisplay: document.querySelector('.identificacion-form .file-name'),
      removeFileBtn: document.querySelector('.identificacion-form .remove-file')
    };

    // 显示/隐藏控制函数
    const toggleViews = (showLogin) => {
      const loginElements = [
        DOM.formsContainer,
        DOM.loginItems,
        DOM.identificar,
        ...DOM.loginButtons
      ];
      
      loginElements.forEach(el => {
        el.style.display = showLogin ? '' : 'none';
      });
      
      DOM.identificacionForm.style.display = showLogin ? 'none' : 'block';
      
      if (showLogin) {
        const activeTab = document.querySelector('.login-items li.active');
        const formType = activeTab.getAttribute('data-form');
        DOM.forms.forEach(form => form.classList.remove('active'));
        document.getElementById(`${formType}-form`).classList.add('active');
      }
    };

    // 初始化选项卡切换
    const initTabs = () => {
      DOM.loginTabs.forEach(item => {
        item.addEventListener('click', function() {
          if (this.classList.contains('active')) return;
          
          DOM.loginTabs.forEach(li => li.classList.remove('active'));
          this.classList.add('active');
          
          const formType = this.getAttribute('data-form');
          DOM.forms.forEach(form => form.classList.remove('active'));
          document.getElementById(`${formType}-form`).classList.add('active');
        });
      });
    };

    // 初始化身份验证切换
    const initAuthToggle = () => {
      DOM.toggleIdentificar.addEventListener('click', function(e) {
        e.preventDefault();
        toggleViews(false);
      });

      DOM.volverLogin.addEventListener('click', function(e) {
        e.preventDefault();
        toggleViews(true);
      });
    };

    // 初始化文件上传功能
const initFileUpload = () => {
  const fileInput = document.getElementById('identificacion-upload');
  const customUploadText = document.querySelector('.custom-upload-text');

  if (!fileInput || !customUploadText) {
    console.warn('缺少文件上传相关元素');
    return;
  }
  
  fileInput.addEventListener('change', function(e) {
    if (this.files.length > 0) {
      const file = this.files[0];
      
      // 更新上传按钮文本为文件名
      customUploadText.textContent = file.name;
      
      // 验证文件大小
      if (file.size > 2.5 * 1024 * 1024) {
        customUploadText.textContent = 'Archivo demasiado grande (Máx 2.5MB)';
        customUploadText.style.color = '#E87A2B';
        this.value = '';
      } else {
        customUploadText.style.color = '#27ae60';
      }
    }
  });
};
    // 表单验证函数
    const initFormValidation = () => {
      DOM.submitIdentificacion.addEventListener('click', function(e) {
        e.preventDefault();
        
        const form = DOM.identificacionForm;
        const inputs = form.querySelectorAll('input[required]');
        const errors = [];
        
        inputs.forEach(input => {
          if (!input.value && input.type !== 'file') {
            const fieldName = input.previousElementSibling?.textContent?.trim() || 'Campo';
            errors.push(`${fieldName} es requerido`);
          }
        });
        
        const fileInput = form.querySelector('input[type="file"]');
        if (fileInput.files.length === 0) {
          errors.push('Documento de identificación es requerido');
        } else {
          const file = fileInput.files[0];
          if (file.type !== 'application/pdf') {
            errors.push('Solo se permiten archivos PDF');
          }
          if (file.size > 2621440) {
            errors.push('El archivo excede el tamaño máximo de 2.5MB');
          }
        }
        
        if (errors.length) {
          alert(errors.join('\n'));
          return;
        }
        
        console.log('Formulario válido, enviando datos...');
        alert('Solicitud enviada. Nos pondremos en contacto con usted.');
        
        setTimeout(() => toggleViews(true), 2000);
      });
    };

    // 初始化所有功能
    const init = () => {
      initTabs();
      initAuthToggle();
      initFileUpload();
      initFormValidation();
      
      // 默认显示学生表单
      document.querySelector('.login-items li[data-form="student"]').click();
    };

    // 执行初始化
    init();
  })();
});