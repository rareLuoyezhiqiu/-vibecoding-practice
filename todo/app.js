// 待办清单 —— 数据保存在浏览器 localStorage 里
const STORAGE_KEY = "vibecoding.todos";

const form = document.getElementById("todo-form");
const input = document.getElementById("todo-input");
const list = document.getElementById("todo-list");
const empty = document.getElementById("empty");
const summary = document.getElementById("summary");
const clearBtn = document.getElementById("clear-completed");
const filterButtons = document.querySelectorAll(".filter");
const counts = {
  all: document.getElementById("count-all"),
  active: document.getElementById("count-active"),
  completed: document.getElementById("count-completed"),
};

let todos = loadTodos();
let currentFilter = "all";

/* ---------- 数据读写 ---------- */

function loadTodos() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const data = raw ? JSON.parse(raw) : [];
    return Array.isArray(data) ? data : [];
  } catch (err) {
    console.warn("读取待办失败，已重置", err);
    return [];
  }
}

function saveTodos() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
}

function createId() {
  if (crypto.randomUUID) return crypto.randomUUID();
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

/* ---------- 操作 ---------- */

function addTodo(text) {
  todos.unshift({
    id: createId(),
    text,
    done: false,
    createdAt: Date.now(),
  });
  saveTodos();
  render();
}

function toggleTodo(id) {
  const todo = todos.find((item) => item.id === id);
  if (!todo) return;
  todo.done = !todo.done;
  saveTodos();
  render();
}

function deleteTodo(id) {
  todos = todos.filter((item) => item.id !== id);
  saveTodos();
  render();
}

function clearCompleted() {
  todos = todos.filter((item) => !item.done);
  saveTodos();
  render();
}

/* ---------- 渲染 ---------- */

function getVisibleTodos() {
  if (currentFilter === "active") return todos.filter((t) => !t.done);
  if (currentFilter === "completed") return todos.filter((t) => t.done);
  return todos;
}

function buildItem(todo) {
  const li = document.createElement("li");
  li.className = "todo-item" + (todo.done ? " done" : "");
  li.dataset.id = todo.id;

  const check = document.createElement("button");
  check.className = "check";
  check.type = "button";
  check.dataset.action = "toggle";
  check.setAttribute("aria-label", todo.done ? "标记为未完成" : "标记为已完成");
  check.setAttribute("aria-pressed", String(todo.done));

  const text = document.createElement("span");
  text.className = "text";
  text.textContent = todo.text;

  const del = document.createElement("button");
  del.className = "delete";
  del.type = "button";
  del.dataset.action = "delete";
  del.setAttribute("aria-label", "删除这条待办");
  del.textContent = "×";

  li.append(check, text, del);
  return li;
}

function render() {
  const visible = getVisibleTodos();

  list.replaceChildren(...visible.map(buildItem));

  const doneCount = todos.filter((t) => t.done).length;
  counts.all.textContent = todos.length;
  counts.active.textContent = todos.length - doneCount;
  counts.completed.textContent = doneCount;

  summary.textContent = todos.length
    ? `共 ${todos.length} 项 · 已完成 ${doneCount} 项`
    : "共 0 项";

  clearBtn.disabled = doneCount === 0;

  if (visible.length === 0) {
    empty.hidden = false;
    empty.textContent = todos.length === 0
      ? "这里空空如也，添加一条待办吧 ✨"
      : "没有符合当前筛选的待办";
  } else {
    empty.hidden = true;
  }
}

/* ---------- 事件 ---------- */

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) {
    input.focus();
    return;
  }
  addTodo(text);
  input.value = "";
  input.focus();
});

list.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const id = button.closest(".todo-item").dataset.id;

  if (button.dataset.action === "toggle") toggleTodo(id);
  if (button.dataset.action === "delete") deleteTodo(id);
});

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    currentFilter = button.dataset.filter;
    filterButtons.forEach((b) => {
      const active = b === button;
      b.classList.toggle("active", active);
      b.setAttribute("aria-selected", String(active));
    });
    render();
  });
});

clearBtn.addEventListener("click", clearCompleted);

/* ---------- 启动 ---------- */

document.getElementById("today").textContent = new Intl.DateTimeFormat(
  "zh-CN",
  { dateStyle: "full" }
).format(new Date());

render();
