# Static builder
FROM node:lts as builder
WORKDIR /gui

COPY gui/package.json gui/yarn.lock ./
RUN yarn install --non-interactive

COPY gui .
RUN yarn build

# Main application container
FROM python:3.9
WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
COPY --from=builder /gui/dist /app/gui/dist

ENTRYPOINT ["python", "main.py"]
