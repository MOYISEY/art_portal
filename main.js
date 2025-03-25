// Функция для обработки лайков проектов
function setupLikeButtons() {
  const likeButtons = document.querySelectorAll(".like-btn")

  likeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const projectId = this.dataset.projectId
      const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value

      fetch(`/projects/like/${projectId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          const likesCountElement = document.getElementById(`likes-count-${projectId}`)
          likesCountElement.textContent = data.likes_count

          if (data.status === "liked") {
            this.classList.add("liked")
            this.querySelector("i").classList.add("text-danger")
          } else {
            this.classList.remove("liked")
            this.querySelector("i").classList.remove("text-danger")
          }
        })
        .catch((error) => console.error("Error:", error))
    })
  })
}

// Функция для обработки комментариев через AJAX
function setupCommentForm() {
  const commentForm = document.getElementById("comment-form")

  if (commentForm) {
    commentForm.addEventListener("submit", function (e) {
      e.preventDefault()

      const formData = new FormData(this)
      const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value

      fetch(this.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            // Создаем элемент нового комментария
            const commentsList = document.getElementById("comments-list")
            const newComment = document.createElement("div")
            newComment.className = "card mb-3"
            newComment.id = `comment-${data.comment_id}`

            // Заполняем содержимое комментария
            newComment.innerHTML = `
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <div class="d-flex align-items-center">
                                    <a href="/users/profile/${data.author_username}/" class="text-decoration-none text-dark">
                                        ${
                                          data.author_avatar
                                            ? `<img src="${data.author_avatar}" alt="${data.author}" class="avatar-sm me-2">`
                                            : `<i class="fas fa-user-circle fa-2x me-2 text-secondary"></i>`
                                        }
                                        <span>${data.author}</span>
                                    </a>
                                </div>
                                <small class="text-muted">${data.created_at}</small>
                            </div>
                            <p class="mb-1">${data.content}</p>
                            <div class="text-end">
                                <form method="post" action="/comments/delete/${data.comment_id}/" class="d-inline">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                    <button type="submit" class="btn btn-sm btn-outline-danger">Удалить</button>
                                </form>
                            </div>
                        </div>
                    `

            // Добавляем новый комментарий в начало списка
            if (commentsList.querySelector(".alert")) {
              commentsList.innerHTML = ""
            }
            commentsList.prepend(newComment)

            // Очищаем форму
            document.getElementById("id_content").value = ""
          }
        })
        .catch((error) => console.error("Error:", error))
    })
  }
}

// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
  setupLikeButtons()
  setupCommentForm()
})

