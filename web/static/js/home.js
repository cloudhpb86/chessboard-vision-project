function handleFileSelect(event) {
    const files = event.target.files;
    const imagePreview1 = document.getElementById('imagePreview1');
    const uploadInstruction = document.getElementById('uploadInstruction');

    // 清空预览框和删除之前的图片
    imagePreview1.innerHTML = '';
    imagePreview1.classList.remove('filled');

const reader = new FileReader();
    reader.onload = function (e) {
        const img = document.createElement('img');
        img.src = e.target.result;
        img.alt = 'Uploaded Image';
        img.classList.add('uploaded');


        // 延迟添加图片到DOM，以便实现淡入效果
        setTimeout(function () {
            imagePreview1.appendChild(img);
            imagePreview1.classList.add('filled');
            uploadInstruction.classList.add('hidden'); // 图片都加载完后隐藏提示
        }, 10); // 稍作延迟以确保过渡效果
};
reader.readAsDataURL(files[0]);
}
//用于侧边栏滑动跳转
document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault(); // 阻止默认行为
            const targetId = link.getAttribute('data-target'); // 获取目标区域的id
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    document.getElementById('result').classList.add('hidden');
});

// 替换 startDetection 函数
function startDetection(event) {
    const files = document.getElementById('imageUpload').files;
    if (files.length === 0) {
        alert('请先上传图片');
        return;
    }

    // 显示加载动画，隐藏结果区域
    document.getElementById('loading').classList.remove('hidden');
    document.querySelector('.result-container').classList.add('hidden');

    const formData = new FormData();
    formData.append('file', files[0]);

    // 上传图片
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('上传失败');
        return response.text();
    })
    .then(() => {
        alert('需要等待30秒左右')
        // 开始处理
        return fetch('/result', {
            method: 'POST'
        });
    })
    .then(response => {
        if (!response.ok) throw new Error('处理失败');
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // 更新图片
            document.getElementById('originalImage').src = data.im1_path;
            document.getElementById('resultImage').src = data.out_path;

            // 显示结果区域，隐藏加载动画
            document.querySelector('.result-container').classList.remove('hidden');
            document.getElementById('loading').classList.add('hidden');

            setTimeout(() => {
                const resultSection = document.getElementById('result');
                resultSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 300);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('处理失败: ' + error.message);
        document.getElementById('loading').classList.add('hidden');
    });
}