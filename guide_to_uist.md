#### Guide to UIST 2019

###### General goals

* What problems are you solving or what opportunities are you seizing?

  *Problems:*

 1. Assessment of user experience in 3D while interacting with objects at different levels of depth.

 2. It is unclear how to switch seamlessly between multiple interactive contexts in mixed reality that are placed at different depths in respect to the user.

 3. Midas touch problem with gaze interaction in 3D. The majority (if not all) solutions to this problem are based on 2D interaction. When we move to 3D, new possibilities to cope with this issue arise.

 4. 3D eye gaze estimation is still unreliable when compared to 2D methods.

    *Opportunities:*

 5. Full or partial gaze-based control over the 3D environment using vergence

 6. Novel interaction techniques that leverage depth and focus depth for selection or context-switching 

 7. Vergence could be a hands-free resource of triggering virtual information in translucent displays without the Midas touch problem, or lack of control and latency typically found in dwell-based selection.

 8. There is also an opportunity to come up with technical solutions to come around the lack of reliability in 3D eye gaze estimation.

    

* What are the previous solutions?

  This theme is virtually unexplored. The only work that investigated the use of gaze focus depth as an interaction modality was proposed by Pai et al. at UIST 2016. However, they only assessed the usability of this technique as a scroll-based mechanism between two planes, which were placed between 5 and 25 m in a VR setting. 

  No new application or use case was actually developed in this case, and no new selection technique was proposed. Besides, gaze ray intersection has been demonstrated to be very unreliable to estimate focus depth. Ideally, accommodation and pupil diameter should also be employed in this case. Moreover, above 5 m of depth, gaze vectors are virtually parallel in any commercial video-based eye tracking system, so it seems that this distance was not scaled properly (e.g., if it was between 0.5 and 2.5 m, it would make much more sense). Finally, this is study was confined to VR and cannot be applied to AR or mixed reality systems, in general.

  Another study that conjectured the use of gaze focus depth for interaction was proposed in a short paper at ISMAR 2015. In this work, authors considered vergence as a response to build a new visualization method that allows for some sort of "X-ray vision".

  

* How (well) can you solve the problem?

  This problem could be solved by leveraging the latest findings in 3D eye gaze estimation, showing that multi feature-based techniques can actually improve focus depth estimation [ETRA 2018], and also that geometry-based procedures provide higher stability while navigating through different depth planes [COGAIN 2018]. With a hybrid approach, it is possible to have a reasonable 3D eye gaze estimation that can support a reliable transition between multiple depth planes.

  Given that we can solve the majority of all technical issues, the next step is to design how we interact using vergence. Simply put, we rarely perform this kind of movement without stimuli, even though it is possible to consciously converge or diverge the eyes in a single direction. Therefore, it sounds sensible to place visual cues in our augmented virtual layer of the world to guide the eyes, so that convergence can be performed seamlessly. These cues could be virtual spheres hovering in the space near a selectable object that show a converging path in the direction of the user once he sits his eyes upon one of these spheres. Another possibility is to show this converging path in respect to the selectable object, that is, once the user fixates over an object, a translucent path with markings is shown, in which the  markings indicate planes of interaction. In the case of translucent physical displays, such as home or car windows, we could overlay virtual information on top of it when the user is actually gazing on them. 

  Vergence could also be a high-latency movement and an uncomfortable one when performed repetitively, thus it is not recommended to design an interaction process in which vergence is used as a rapid selection mechanism. Thus, we see it as more suitable to discriminate unambiguously different interactive contexts, in a way, similar to a "toggle" button. Using like that, we can transit between multiple depths without the explicit indication through gestures, mechanical switches, or other kind of toggling.

  When moving between planes, vergence could also have a secondary role as a selection mechanism that does not rely on dwell-time or is subject to the Midas touch problem -- at least not in the same level as other 2D techniques. By fixating on some button shown on a virtual plane and then diverging the eyes to focus on a physical device linked to this plane, we could trigger this button function without explicit gestures. It is as if almost we were using the Midas touch problem for selection.

  

* What is the main contribution of this work to the field?

  The main contribution would be a hands-free interaction technique that is based on multiple depth interfacing. The key feature would be the use of vergence to his end. Such choice also implicates other secondary contributions, such as:

  * technical improvements over 3D eye gaze estimation

  * design of vergence-based interfaces (Pai et al. suggested it, but they have never done it)

    

###### Paper-related

* Is the paper complete?

* Does the paper contain too much information?

* Can this paper be presented well?

* Does this paper present good quality?

  
