# Pooma

Ray marching graphics library.

Из-за того, что в текстуре спрайта могут быть дырки(и выступы по бокам), за которыми 1D stencil buffer откинет текстуры,
мы вынуждены рендерить все. Каждый этап рисует свою картинку независимо, после чего картинка силивается через буффер
глубин. Буффер глубины не решит проблему с дырками, если сначала рисовть спрайты, а затем - стены.

2D stencil buffer может быть слишком ресурсоемким решением даже для Cython кода. Нужно будет проходить > 2*10^6 px за
1/16s + затраты на отправку на GPU, обновление физики, AI, etc.

```mermaid
flowchart LR;
    BC[Buffer clears] -->|surface| CW
    ISB[Init stencil buffer] -->|stencil| CW
    
    subgraph FR["Frame Rendering(Pipeline)"];
        direction LR;
        subgraph Cython;
            direction LR;
            CW[cast_walls] -->|stencil| CS[cast_sprites];
            CW -->|surface| CS
        end
        CS -->|surface| FPS
        CS -->|stencil| FPS
    end
    
    FPS -->|surface| DF[Display filps]
```
